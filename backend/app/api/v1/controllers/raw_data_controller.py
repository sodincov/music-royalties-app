# app/api/v1/controllers/raw_data_controller.py
import io
from io import BytesIO
from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import pandas as pd
import numpy as np
from decimal import Decimal # Импортируем Decimal

from app.database import DBSessionDep
from app.sqlmodels.raw_excel_data import ExcelReport, RawUsageDataStrict # Обновляем импорт
# Импортируем новые модели ответов
from app.api.v1.models.raw_data import (
    ExcelReportResponse, RawUsageDataResponse, UploadRawReportResponse,
    DeleteReportResponse, GetReportInfoResponse
)

def safe_str(value) -> Optional[str]:
    """Преобразует значение из Excel в безопасную строку или None."""
    if pd.isna(value) or value == "":
        return None
    return str(value).strip()

def safe_decimal(value, default: Decimal = Decimal('0.0')) -> Decimal:
    """Безопасное преобразование в Decimal."""
    if pd.isna(value):
        return default
    try:
        return Decimal(str(value)) # Сначала в строку, потом в Decimal, чтобы избежать проблем с float
    except (ValueError, TypeError):
        return default

def safe_float(value, default: float = 0.0) -> float:
    """Безопасное преобразование в float."""
    if pd.isna(value):
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default: int = 0) -> int:
    """Безопасное преобразование в int."""
    if pd.isna(value):
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

class RawDataController:
    def __init__(self, db_session: DBSessionDep):
        self.db_session = db_session

    async def process_and_upload_raw_report(self, file: UploadFile, description: Optional[str] = None) -> UploadRawReportResponse:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Файл должен быть в формате .xlsx или .xls")

        try:
            # 1. Создаем запись об отчете
            excel_report = ExcelReport(
                filename=file.filename,
                original_name=file.filename, # Сохраняем оригинальное имя
                description=description or f"Загруженный файл: {file.filename}"
            )
            self.db_session.add(excel_report)
            # flush, чтобы получить ID отчета до commit
            await self.db_session.flush()

            # 2. Читаем Excel-файл
            file_content = await file.read()
            df = pd.read_excel(BytesIO(file_content), dtype=object) # dtype=object, чтобы сохранить типы как есть

            # 3. Сохраняем каждую строку в RawUsageDataStrict
            for index, row in df.iterrows():
                # Сопоставляем колонки Excel с полями модели RawUsageDataStrict
                # Используем safe_* функции для безопасного преобразования
                raw_data_entry = RawUsageDataStrict(
                    excel_report_id=excel_report.id,
                    row_index=index,
                    # Сопоставление колонок Excel с полями модели
                    period=safe_str(row.get('Период использования')), # Используем .get() для безопасности
                    platform=safe_str(row.get('Площадка')),
                    right_type=safe_str(row.get('Тип прав')),
                    territory=safe_str(row.get('Территория')),
                    content_type=safe_str(row.get('Тип контента')),
                    usage_type=safe_str(row.get('Вид использования')),
                    performer_name_excel=safe_str(row.get('Исполнитель')),
                    track_title_excel=safe_str(row.get('Название трека')),
                    album_title_excel=safe_str(row.get('Название альбома')),
                    author_words_name_excel=safe_str(row.get('Автор слов')),
                    author_music_name_excel=safe_str(row.get('Автор музыки')),
                    licensor_share_author_percent=safe_decimal(row.get('Доля авторских прав Лицензиара')),
                    licensor_share_neighboring_percent=safe_decimal(row.get('Доля смежных прав Лицензиара')),
                    isrc=safe_str(row.get('ISRC')),
                    upc=safe_str(row.get('UPC')),
                    copyright=safe_str(row.get('Копирайт')),
                    quantity=safe_int(row.get('Количество')),
                    total_royalty_author=safe_decimal(row.get('Сумма денежных средств, полученных ЛИЦЕНЗИАТОМ за авторские права')),
                    total_royalty_neighboring=safe_decimal(row.get('Сумма денежных средств, полученных ЛИЦЕНЗИАТОМ за смежные права')),
                    licensor_share_author_licensor_percent=safe_decimal(row.get('Доля монетизации Лицензиара авторских прав')), # Предполагаемое имя колонки
                    licensor_share_neighboring_licensor_percent=safe_decimal(row.get('Доля монетизации Лицензиара смежных прав')), # Предполагаемое имя колонки
                    calculated_royalty_author=safe_decimal(row.get('Вознаграждение ЛИЦЕНЗИАРА за авторские права')), # Предполагаемое имя колонки
                    calculated_royalty_neighboring=safe_decimal(row.get('Вознаграждение ЛИЦЕНЗИАРА за смежные права')), # Предполагаемое имя колонки
                    calculated_total_royalty=safe_decimal(row.get('Итого вознаграждение ЛИЦЕНЗИАРА')) # Предполагаемое имя колонки
                    # Добавь сопоставление для других колонок, если они есть в Excel
                )
                self.db_session.add(raw_data_entry)

            await self.db_session.commit()
            return UploadRawReportResponse(
                message=f"Файл '{file.filename}' успешно загружен и сохранен как отчет ID {excel_report.id}",
                report_id=excel_report.id
            )

        except Exception as e:
            await self.db_session.rollback()
            print(f"Ошибка при обработке файла: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка сервера при обработке файла: {str(e)}")

    # Метод для получения списка всех загруженных отчетов
    async def get_all_reports(self) -> List[ExcelReportResponse]:
        result = await self.db_session.execute(select(ExcelReport))
        reports = result.scalars().all()
        return [
            ExcelReportResponse(
                id=r.id,
                filename=r.filename,
                original_name=r.original_name,
                upload_date=r.upload_date,
                upload_status=r.upload_status,
                description=r.description
            )
            for r in reports
        ]

    # Метод для получения "сырых" данных по ID отчета
    # Возвращаем словари с конкретными полями модели, а не JSON
    async def get_raw_data_by_report_id(self, report_id: int) -> List[RawUsageDataResponse]:
        result = await self.db_session.execute(
            select(RawUsageDataStrict).where(RawUsageDataStrict.excel_report_id == report_id)
        )
        raw_data_entries = result.scalars().all()
        return [
            RawUsageDataResponse(
                id=r.id,
                row_index=r.row_index,
                period=r.period,
                platform=r.platform,
                right_type=r.right_type,
                territory=r.territory,
                content_type=r.content_type,
                usage_type=r.usage_type,
                performer_name_excel=r.performer_name_excel,
                track_title_excel=r.track_title_excel,
                album_title_excel=r.album_title_excel,
                author_words_name_excel=r.author_words_name_excel,
                author_music_name_excel=r.author_music_name_excel,
                licensor_share_author_percent=r.licensor_share_author_percent,
                licensor_share_neighboring_percent=r.licensor_share_neighboring_percent,
                isrc=r.isrc,
                upc=r.upc,
                copyright=r.copyright,
                quantity=r.quantity,
                total_royalty_author=r.total_royalty_author,
                total_royalty_neighboring=r.total_royalty_neighboring,
                licensor_share_author_licensor_percent=r.licensor_share_author_licensor_percent,
                licensor_share_neighboring_licensor_percent=r.licensor_share_neighboring_licensor_percent,
                calculated_royalty_author=r.calculated_royalty_author,
                calculated_royalty_neighboring=r.calculated_royalty_neighboring,
                calculated_total_royalty=r.calculated_total_royalty,
                processed_status=r.processed_status,
            )
            for r in raw_data_entries
        ]

    # Опционально: метод для получения информации о конкретном отчете
    async def get_report_info(self, report_id: int) -> GetReportInfoResponse:
        result = await self.db_session.execute(
            select(ExcelReport).where(ExcelReport.id == report_id)
        )
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Отчет не найден")
        return GetReportInfoResponse(
            id=report.id,
            filename=report.filename,
            original_name=report.original_name,
            upload_date=report.upload_date,
            upload_status=report.upload_status,
            description=report.description
        )

    # --- Обновлённый метод для удаления отчета ---
    # Обновляем имя модели в запросах
    async def delete_report(self, report_id: int) -> DeleteReportResponse:
        """
        Удаляет отчет и все связанные с ним 'сырые' данные (строго типизированные).
        """
        # Проверяем, существует ли отчет
        report_info = await self.get_report_info(report_id) # get_report_info теперь выбрасывает 404, если не найден

        try:
            # Удаляем все связанные строки из raw_usage_data_strict
            stmt_raw_data = delete(RawUsageDataStrict).where(RawUsageDataStrict.excel_report_id == report_id)
            await self.db_session.execute(stmt_raw_data)

            # Затем удаляем сам отчет из excel_reports
            stmt_report = delete(ExcelReport).where(ExcelReport.id == report_id)
            await self.db_session.execute(stmt_report)

            await self.db_session.commit()
            return DeleteReportResponse(
                message=f"Отчет ID {report_id} и все связанные с ним 'сырые' данные успешно удалены.",
                deleted_report_id=report_id
            )
        except Exception as e:
            await self.db_session.rollback()
            print(f"Ошибка при удалении отчета ID {report_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Ошибка сервера при удалении отчета: {str(e)}")


# ✅ ФИНАЛЬНАЯ СТРОКА: только DBSessionDep
from typing import Annotated
from fastapi import Depends

RawDataControllerDep = Annotated["RawDataController", Depends(RawDataController)]
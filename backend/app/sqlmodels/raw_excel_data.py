# app/sqlmodels/raw_excel_data.py
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship # Импортируем из SQLModel
from sqlalchemy import Column # Для указания специфичных типов колонок
from sqlalchemy import Numeric # Импортируем Numeric из SQLAlchemy
from datetime import datetime
from decimal import Decimal # Для денежных значений

if TYPE_CHECKING:
    from app.sqlmodels import Person, Track # Импорт для типизации, если они определены в другом месте

class ExcelReport(SQLModel, table=True):
    __tablename__ = 'excel_reports'

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    filename: str = Field(nullable=False) # Имя файла на сервере
    original_name: str = Field(nullable=False) # Оригинальное имя файла
    upload_date: datetime = Field(default_factory=datetime.utcnow, nullable=False) # Используем datetime.utcnow
    upload_status: str = Field(default='completed') # 'processing', 'completed', 'failed'
    description: Optional[str] = Field(default=None) # Необязательное описание

    # Связь: один отчет -> много строк данных
    # back_populates указывает на атрибут в RawUsageData
    raw_data_entries: list["RawUsageDataStrict"] = Relationship(back_populates="excel_report") # Обновим имя модели

    def __repr__(self):
        return f"<ExcelReport(id={self.id}, filename='{self.filename}', original_name='{self.original_name}')>"

# --- НОВАЯ МОДЕЛЬ СТРОГО ТИПИЗИРОВАННЫХ СЫРЫХ ДАННЫХ ---
class RawUsageDataStrict(SQLModel, table=True): # Переименуем модель для ясности
    __tablename__ = 'raw_usage_data_strict' # Переименуем таблицу

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    excel_report_id: int = Field(nullable=False, foreign_key="excel_reports.id", index=True) # Индекс для быстрого поиска по отчету
    row_index: int = Field(nullable=False) # Индекс строки в исходном файле

    # --- Поля из Excel ---
    # Период использования
    period: Optional[str] = Field(default=None)
    # Площадка
    platform: Optional[str] = Field(default=None)
    # Тип прав
    right_type: Optional[str] = Field(default=None)
    # Территория
    territory: Optional[str] = Field(default=None)
    # Тип контента
    content_type: Optional[str] = Field(default=None)
    # Вид использования
    usage_type: Optional[str] = Field(default=None)
    # Исполнитель
    performer_name_excel: Optional[str] = Field(default=None)
    # Название трека
    track_title_excel: Optional[str] = Field(default=None)
    # Название альбома
    album_title_excel: Optional[str] = Field(default=None)
    # Автор слов
    author_words_name_excel: Optional[str] = Field(default=None)
    # Автор музыки
    author_music_name_excel: Optional[str] = Field(default=None)
    # Доля авторских прав Лицензиара (в Excel это, вероятно, доля в %, например, 0.5 для 50%)
    licensor_share_author_percent: Optional[Decimal] = Field(sa_column=Column("licensor_share_author_percent", Numeric(precision=10, scale=4), nullable=True))
    # Доля смежных прав Лицензиара
    licensor_share_neighboring_percent: Optional[Decimal] = Field(sa_column=Column("licensor_share_neighboring_percent", Numeric(precision=10, scale=4), nullable=True))
    # ISRC
    isrc: Optional[str] = Field(default=None)
    # UPC (может быть длинным числом, лучше строка)
    upc: Optional[str] = Field(default=None)
    # Копирайт
    copyright: Optional[str] = Field(default=None)
    # Количество
    quantity: Optional[int] = Field(default=None)
    # Сумма денежных средств, полученных ЛИЦЕНЗИАТОМ за авторские права
    total_royalty_author: Optional[Decimal] = Field(sa_column=Column("total_royalty_author", Numeric(precision=15, scale=4), nullable=True))
    # Сумма денежных средств, полученных ЛИЦЕНЗИАТОМ за смежные права
    total_royalty_neighboring: Optional[Decimal] = Field(sa_column=Column("total_royalty_neighboring", Numeric(precision=15, scale=4), nullable=True))
    # Доля монетизации Лицензиара авторских прав (предполагаем, что есть в Excel)
    licensor_share_author_licensor_percent: Optional[Decimal] = Field(sa_column=Column("licensor_share_author_licensor_percent", Numeric(precision=10, scale=4), nullable=True))
    # Доля монетизации Лицензиара смежных прав
    licensor_share_neighboring_licensor_percent: Optional[Decimal] = Field(sa_column=Column("licensor_share_neighboring_licensor_percent", Numeric(precision=10, scale=4), nullable=True))

    # --- Новые поля, которые могут быть в Excel ---
    # Вознаграждение ЛИЦЕНЗИАРА за авторские права (если рассчитывается в Excel)
    calculated_royalty_author: Optional[Decimal] = Field(sa_column=Column("calculated_royalty_author", Numeric(precision=15, scale=4), nullable=True))
    # Вознаграждение ЛИЦЕНЗИАРА за смежные права
    calculated_royalty_neighboring: Optional[Decimal] = Field(sa_column=Column("calculated_royalty_neighboring", Numeric(precision=15, scale=4), nullable=True))
    # Итого вознаграждение ЛИЦЕНЗИАРА
    calculated_total_royalty: Optional[Decimal] = Field(sa_column=Column("calculated_total_royalty", Numeric(precision=15, scale=4), nullable=True))

    # Статус обработки строки (остаётся)
    processed_status: str = Field(default='pending') # 'pending', 'matched', 'unmatched'

    # Связь: одна строка данных <- один отчет
    excel_report: "ExcelReport" = Relationship(back_populates="raw_data_entries")

    def __repr__(self):
        return f"<RawUsageDataStrict(id={self.id}, report_id={self.excel_report_id}, row_index={self.row_index}, isrc='{self.isrc}')>"

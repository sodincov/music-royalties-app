# app/api/v1/routers/raw_data.pyfrom typing import List
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query, Path, status

from app.api.v1.controllers.raw_data_controller import RawDataControllerDep
from app.deps import AuthUserDep

# Импортируем модели запросов/ответов
from app.api.v1.models.raw_data import (
    UploadRawReportRequest, UploadRawReportResponse,
    ExcelReportResponse, GetReportInfoResponse,
    RawUsageDataResponse, DeleteReportResponse
)

router = APIRouter(prefix="/raw-data", tags=["raw_data"])

@router.post("/", response_model=UploadRawReportResponse)
async def upload_raw_report(
    file: UploadFile = File(...),
    description: str = Query(None, description="Описание отчета (например, '3 квартал 2025')"),
    controller: RawDataControllerDep = Depends(),
    current_user: AuthUserDep = Depends(), # Добавляем проверку аутентификации/авторизации
) -> UploadRawReportResponse:
    """
    Загружает Excel-файл и сохраняет его содержимое в таблицу raw_usage_data_strict,
    связывая с новой записью в excel_reports.
    """
    # В контроллере мы не используем current_user, но можно добавить логику проверки прав
    return await controller.process_and_upload_raw_report(file, description=description)

@router.get("/", response_model=List[ExcelReportResponse])
async def list_all_reports(
    controller: RawDataControllerDep = Depends(),
    current_user: AuthUserDep = Depends(), # Добавляем проверку аутентификации/авторизации
) -> List[ExcelReportResponse]:
    """
    Возвращает список всех загруженных отчетов.
    """
    # В контроллере мы не используем current_user, но можно добавить логику проверки прав
    return await controller.get_all_reports()

@router.get("/{report_id}", response_model=GetReportInfoResponse)
async def get_report_info(
    report_id: int = Path(..., description="ID отчета"),
    controller: RawDataControllerDep = Depends(),
    current_user: AuthUserDep = Depends(), # Добавляем проверку аутентификации/авторизации
) -> GetReportInfoResponse:
    """
    Возвращает информацию о конкретном загруженном отчете.
    """
    # В контроллере мы не используем current_user, но можно добавить логику проверки прав
    return await controller.get_report_info(report_id)

@router.get("/{report_id}/raw-data", response_model=List[RawUsageDataResponse])
async def get_raw_data_for_report(
    report_id: int = Path(..., description="ID отчета"),
    controller: RawDataControllerDep = Depends(),
    current_user: AuthUserDep = Depends(), # Добавляем проверку аутентификации/авторизации
) -> List[RawUsageDataResponse]:
    """
    Возвращает 'сырые' данные для конкретного отчета.
    """
    # В контроллере мы не используем current_user, но можно добавить логику проверки прав
    return await controller.get_raw_data_by_report_id(report_id)

# --- Новый эндпоинт для удаления отчета ---
@router.delete("/{report_id}", response_model=DeleteReportResponse)
async def delete_report(
    report_id: int = Path(..., description="ID отчета для удаления"),
    controller: RawDataControllerDep = Depends(),
    current_user: AuthUserDep = Depends(), # Добавляем проверку аутентификации/авторизации
) -> DeleteReportResponse:

    return await controller.delete_report(report_id)

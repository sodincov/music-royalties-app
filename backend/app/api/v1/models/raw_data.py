# app/api/v1/models/raw_data.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# --- Модели запросов ---

class UploadRawReportRequest(BaseModel):
    description: Optional[str] = None
    # file: UploadFile # Не указываем файл в модели Pydantic, он передаётся отдельно в роутере

class GetRawDataByReportIdRequest(BaseModel):
    report_id: int

class GetReportInfoRequest(BaseModel):
    report_id: int

class DeleteReportRequest(BaseModel):
    report_id: int

# --- Модели ответов ---

class ExcelReportResponse(BaseModel):
    id: int
    filename: str
    original_name: str
    upload_date: datetime
    upload_status: str
    description: Optional[str]

class RawUsageDataResponse(BaseModel):
    id: int
    row_index: int
    period: Optional[str]
    platform: Optional[str]
    right_type: Optional[str]
    territory: Optional[str]
    content_type: Optional[str]
    usage_type: Optional[str]
    performer_name_excel: Optional[str]
    track_title_excel: Optional[str]
    album_title_excel: Optional[str]
    author_words_name_excel: Optional[str]
    author_music_name_excel: Optional[str]
    licensor_share_author_percent: Optional[Decimal]
    licensor_share_neighboring_percent: Optional[Decimal]
    isrc: Optional[str]
    upc: Optional[str]
    copyright: Optional[str]
    quantity: Optional[int]
    total_royalty_author: Optional[Decimal]
    total_royalty_neighboring: Optional[Decimal]
    licensor_share_author_licensor_percent: Optional[Decimal]
    licensor_share_neighboring_licensor_percent: Optional[Decimal]
    calculated_royalty_author: Optional[Decimal]
    calculated_royalty_neighboring: Optional[Decimal]
    calculated_total_royalty: Optional[Decimal]
    processed_status: str

class UploadRawReportResponse(BaseModel):
    message: str
    report_id: int

class DeleteReportResponse(BaseModel):
    message: str
    deleted_report_id: int

class GetReportInfoResponse(ExcelReportResponse):
    pass # ExcelReportResponse уже содержит все нужные поля

class GetRawDataByReportIdResponse(RawUsageDataResponse):
    pass # RawUsageDataResponse уже содержит все нужные поля


from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class UsageReport(SQLModel, table=True):
    __tablename__ = "usage_report"

    id: int = Field(default=None, primary_key=True)

    # --- Данные из Excel ---
    period: str # "Период использования" (например, '2025-04', '3 кв 2025')
    platform: str # "Площадка" (например, 'TikTok', 'Яндекс Музыка')
    right_type: Optional[str] = Field(default=None)
    territory: str # "Территория" (например, 'Россия', 'США')
    content_type: str # "Тип контента" (например, 'Трек', 'Фуллтрек')
    usage_type: str # "Вид использования" (например, 'Подписка', 'Синхронизация')
    performer_name_excel: str # "Исполнитель" из Excel (например, 'VICTORIA BRIUS')
    track_title_excel: str # "Название трека" из Excel (например, 'Твоя фамилия')
    album_title_excel: str # "Название альбома" из Excel (например, 'Твоя фамилия')
    author_words_name_excel: str # "Автор слов" из Excel (например, 'Золотова Виктория')
    author_music_name_excel: str # "Автор музыки" из Excel (например, 'Золотова Виктория')
    licensor_share_author_percent: float # "Доля авторских прав Лицензиара" (например, 100.0)
    licensor_share_neighboring_percent: float # "Доля смежных прав Лицензиара" (например, 100.0)
    isrc: str # "ISRC" (например, 'RUA1D2263720'), может быть уникальным
    upc: Optional[str] = None # "UPC" (например, '5063018366211')
    copyright: str # "Копирайт" (например, 'Music Chard')
    quantity: int # "Количество" (например, 3)
    total_royalty_author: float # "Сумма денежных средств, полученных ЛИЦЕНЗИАТОМ за авторские права" (например, 0.00)
    total_royalty_neighboring: float # "Сумма денежных средств, полученных ЛИЦЕНЗИАТОМ за смежные права" (например, 0.12)
    licensor_share_author_licensor_percent: float # "Доля Лицензиара авторских прав" (например, 0.0)
    licensor_share_neighboring_licensor_percent: float # "Доля Лицензиара смежных прав" (например, 0.0)

    # --- Ссылки на сущности в вашей базе данных ---
    track_id: Optional[int] = Field(default=None, foreign_key="track.id") # Ссылка на трек из вашей таблицы track (по ISRC)
    performer_id: Optional[int] = Field(default=None, foreign_key="person.id") # Ссылка на исполнителя из вашей таблицы person
    author_words_id: Optional[int] = Field(default=None, foreign_key="person.id") # Ссылка на автора слов из вашей таблицы person
    author_music_id: Optional[int] = Field(default=None, foreign_key="person.id") # Ссылка на автора музыки из вашей таблицы person

    # --- Рассчитанные столбцы для отчета по человеку ---
    calculated_royalty_author: Optional[float] = None # "Вознаграждение ЛИЦЕНЗИАРА за авторские права" (рассчитывается)
    calculated_royalty_neighboring: Optional[float] = None # "Вознаграждение ЛИЦЕНЗИАРА за смежные права" (рассчитывается)
    calculated_total_royalty: Optional[float] = None # "Итого вознаграждение ЛИЦЕНЗИАРА" (рассчитывается)

    # --- Связи (опционально, для удобства в коде) ---
    # Указываем строковые имена моделей для избежания циклического импорта
    track: Optional["Track"] = Relationship(back_populates="usage_reports")
    performer: Optional["Person"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[UsageReport.performer_id]"})
    author_words: Optional["Person"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[UsageReport.author_words_id]"})
    author_music: Optional["Person"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[UsageReport.author_music_id]"})

    def __repr__(self):
        return f"<UsageReport for Track ISRC: {self.isrc}, Period: {self.period}>"


from pydantic import BaseModel
from typing import Optional

class PersonUsageReportItem(BaseModel):
    period: str
    platform: str
    right_type: Optional[str] = None
    territory: Optional[str] = None
    content_type: str
    usage_type: Optional[str] = None
    performer_name_excel: Optional[str] = None
    track_title_excel: str
    album_title_excel: Optional[str] = None
    author_words_name_excel: Optional[str] = None
    author_music_name_excel: Optional[str] = None
    isrc: str
    upc: Optional[str] = None
    quantity: int
    calculated_royalty_author: float
    calculated_royalty_neighboring: float
    calculated_total_royalty: float

    class Config:
        from_attributes = True  # для SQLModel

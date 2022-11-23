from datetime import datetime
from typing import Union

from pydantic import BaseModel, Field
from pydantic.types import UUID


class StockRecordModelDTO(BaseModel):
    class Config:
        orm_mode = True

    stock_record_id: UUID
    product_id: str
    change_source_id: Union[str, None]
    quantity_change: float
    quantity_change_direction: int
    quantity_before: float
    quantity_actual: float
    change_datetime: datetime


class QueryRequestModelDTO(BaseModel):
    rows: int = Field(default=10, gt=9, le=30)
    offset: int = Field(default=10, gt=-1)
    sortField: Union[str, None] = None
    sortOrder: Union[int, None] = None


class StockRecordQueryResponseModelDTO(BaseModel):
    class Config:
        orm_mode = True

    result: list[StockRecordModelDTO]
    page: int
    total_pages_count: int
    total_records_count: int
    records_per_page_count: int
    is_next: bool
    is_prev: bool

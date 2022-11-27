import json
from typing import Union

from pydantic import BaseModel, Field, validator
from datetime import datetime

from pydantic.utils import to_lower_camel
from typing_extensions import Annotated


class DocumentItem(BaseModel):
    product_id: str
    quantity: float
    price: float
    product_name: str
    quantitative_unit: Union[str, None]

    class Config:
        alias_generator = to_lower_camel


def extract_id(raw_id: str) -> str:
    return json.loads(raw_id)['$oid']


class Document(BaseModel):
    partner_name: str
    validate_stock_availability: bool
    direction: int
    id: Annotated[str, Field(alias='_id', )]
    price: float
    owner: str
    status: str
    date: datetime
    items: list[DocumentItem]

    # custom input conversion for that field
    _normalize_id = validator(
        "id",
        allow_reuse=True)(extract_id)

    class Config:
        alias_generator = to_lower_camel

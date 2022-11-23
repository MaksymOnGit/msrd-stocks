from pydantic import BaseModel
from pydantic.class_validators import Union


class MongoBase(BaseModel):
    operation_type: str
    document_key: Union[str, None]
    full_document: Union[dict, None]

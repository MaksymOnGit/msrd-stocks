import enum
import uuid

from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String, Float, DateTime

from msrdstocks.db.base import Base


class DocumentStatusRecordModel(Base):
    __tablename__ = "document_statuses"

    document_id = Column(String(length=100), nullable=False, primary_key=True)
    status = Column(String(length=100), nullable=False)
    created = Column(DateTime(), nullable=False)
    updated = Column(DateTime(), nullable=False)

class DocumentStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    ACCEPTED = "ACCEPTED"
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"
    UNKNOWN_ITEMS = "UNKNOWN_ITEMS"
    DUPLICATE_ITEMS = "DUPLICATE_ITEMS"
    REJECTED = "REJECTED"

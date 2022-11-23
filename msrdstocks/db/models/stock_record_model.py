import uuid

from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String, Float, DateTime

from msrdstocks.db.base import Base
from msrdstocks.db.models.document_status import DocumentStatusRecordModel


class StockRecordModel(Base):
    __tablename__ = "stock_records"

    stock_record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(length=24), nullable=False)
    change_source_id = Column(String(length=100), ForeignKey(DocumentStatusRecordModel.document_id), nullable=True)
    quantity_change = Column(Float(precision=2, asdecimal=True), nullable=False)
    quantity_change_direction = Column(Integer(), nullable=False)
    quantity_before = Column(Float(precision=2, asdecimal=True), nullable=False)
    quantity_actual = Column(Float(precision=2, asdecimal=True), nullable=False)
    change_datetime = Column(DateTime(), nullable=False)
    previous_stock_record_id = Column(UUID(as_uuid=True), ForeignKey("stock_records.stock_record_id"), unique=True, nullable=True)

    __table_args__ = (
        UniqueConstraint('product_id', 'change_source_id',
                         name='product_id__change_source_id_uniqe'),
    )

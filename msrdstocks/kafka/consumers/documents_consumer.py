from confluent_kafka import DeserializingConsumer
from pydantic import BaseModel

from msrdstocks.db.dao.stock_record_dao import StockRecordDAO
from msrdstocks.db.models.document_status import DocumentStatus
from msrdstocks.dto.document_dto import Document
from msrdstocks.kafka.dependencies import get_kafka_consumer, get_db_session
from msrdstocks.kafka.models.mongo_base import MongoBase


class Product(BaseModel):
    product_id: str


async def documents_consumer():
    async with get_kafka_consumer() as consumer:
        des_cons: DeserializingConsumer = consumer
        des_cons.subscribe(["MsrdDocuments.documents"])
        while True:
            msg = des_cons.poll(timeout=1)
            if msg is None:
                continue

            mongo_base: MongoBase = msg.value()

            if mongo_base.operation_type == 'insert':
                try:
                    doc = Document(**mongo_base.full_document)
                    result = await process_document(doc)
                    if not result:
                        continue
                except Exception:
                    raise

            consumer.commit(asynchronous=True)


async def process_document(doc: Document) -> bool:
    async with get_db_session() as session:
        doc_status = await StockRecordDAO(session).get_document_status_record(doc.id)
        if doc_status is not None:
            return True

        if len(set(o.product_id for o in doc.items)) != len(doc.items):
            await StockRecordDAO(session).set_document_status_record(doc.id, DocumentStatus.DUPLICATE_ITEMS)
            return False

        return await StockRecordDAO(session).create_incoming_stock_record(doc)

from confluent_kafka import DeserializingConsumer
from pydantic import BaseModel

from msrdstocks.db.dao.stock_record_dao import StockRecordDAO
from msrdstocks.kafka.dependencies import get_kafka_consumer, get_db_session
from msrdstocks.kafka.models.mongo_base import MongoBase


class Product(BaseModel):
    product_id: str


async def products_consumer():
    async with get_kafka_consumer() as consumer:
        des_cons: DeserializingConsumer = consumer
        des_cons.subscribe(["MsrdProducts.products"])
        while True:
            msg = des_cons.poll(timeout=1)
            if msg is None:
                continue

            mongo_base: MongoBase = msg.value()

            if mongo_base.operation_type == 'insert':
                async with get_db_session() as session:
                    await StockRecordDAO(session).create_new_stock_record(
                        mongo_base.document_key)
            consumer.commit(asynchronous=True)

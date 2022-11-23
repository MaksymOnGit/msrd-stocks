import json
from typing import Generator

from confluent_kafka import Consumer, KafkaError, Message
from loguru import logger

from msrdstocks.kafka.models.mongo_base import MongoBase


def commit_completed(err, partitions):
    if err:
        logger.error(str(err))
    else:
        logger.info("Committed partition offsets: " + str(partitions))


def consume(cons: Consumer,
            timeout: float) -> Generator[Message, None, None]:
    while True:
        message = cons.poll(timeout)
        if message is None:
            continue

        if message.error():
            if message.error().code() == KafkaError._PARTITION_EOF:
                logger.error('{} [{}] reached end at offset {}\n', message.topic(), message.partition(), message.offset())
                continue
            logger.error("Consumer error: {}".format(message.error()))
            continue
        yield message
    cons.close()


def map_to_base(obj, ctx) -> [MongoBase, None]:
    if obj is None:
        return None
    return MongoBase(document_key=json.loads(obj['documentKey']['_id'])['$oid'] if obj['documentKey'] != None else None,
                     operation_type=obj['operationType'],
                     full_document=obj['fullDocument'])

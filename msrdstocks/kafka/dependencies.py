from asyncio import current_task
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from sqlalchemy.ext.asyncio import (AsyncSession, create_async_engine,
                                    async_scoped_session)
from sqlalchemy.orm import sessionmaker

from msrdstocks.kafka.util import commit_completed, map_to_base
from msrdstocks.settings import settings
from loguru import logger


@asynccontextmanager
async def get_kafka_consumer() -> AsyncGenerator[DeserializingConsumer, None]:
    sr_client = SchemaRegistryClient({'url': settings.kafka_schemaregistry_client})

    deserializer = AvroDeserializer(sr_client, from_dict=map_to_base)

    conf = {'bootstrap.servers': ",".join(settings.kafka_bootstrap_servers),
            'group.id': settings.kafka_consumer_group,
            'enable.auto.commit': False,
            'auto.offset.reset': 'earliest',
            'on_commit': commit_completed,
            'value.deserializer': deserializer
            }

    consumer = DeserializingConsumer(conf)
    logger.info("Consumer created: " + str(conf))

    try:
        yield consumer
    except Exception as e:
        logger.error("Kafka consumer error. Exception {}", e)
        raise
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
        logger.info("Consumer closed: " + str(conf))


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_scoped_session(
        sessionmaker(
            engine,
            expire_on_commit=False,
            class_=AsyncSession,
        ),
        scopefunc=current_task,
    )

    session: AsyncSession = session_factory()

    try:  # noqa: WPS501
        yield session
    except Exception as ex:
        await session.rollback()
        logger.error("Rollback. Session: {} Exception: {}", session, ex)
        raise
    finally:
        await session.close()

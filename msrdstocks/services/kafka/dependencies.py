from aiokafka import AIOKafkaProducer
from fastapi import Request, FastAPI
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession


def get_kafka_producer(request: Request) -> AIOKafkaProducer:  # pragma: no cover
    """
    Returns kafka producer.

    :param request: current request.
    :return: kafka producer from the state.
    """
    return request.app.state.kafka_producer


async def get_db_session(app: FastAPI) -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = app.state.db_session_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()

import asyncio

import uvicorn

from msrdstocks.kafka.consumers.documents_consumer import documents_consumer
from msrdstocks.kafka.consumers.products_consumer import products_consumer
from msrdstocks.settings import settings, AppMode


def main() -> None:
    """Entrypoint of the application."""

    if settings.app_mode == AppMode.PRODUCT_CONSUMER:
        asyncio.run(products_consumer())
        return

    if settings.app_mode == AppMode.DOCUMENT_CONSUMER:
        asyncio.run(documents_consumer())
        return

    uvicorn.run(
        "msrdstocks.web.application:get_app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.value.lower(),
        factory=True,
    )


if __name__ == "__main__":
    main()

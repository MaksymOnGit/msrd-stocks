import asyncio
import uuid
from datetime import datetime

from fastapi import Depends
from loguru import logger
from sqlalchemy import exc, select, func, bindparam, union, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count
from sqlalchemy.types import String, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID

from msrdstocks.db.dependencies import get_db_session
from msrdstocks.db.models.document_status import (DocumentStatusRecordModel,
                                                  DocumentStatus)
from msrdstocks.db.models.stock_record_model import StockRecordModel
from msrdstocks.dto.document_dto import Document
from msrdstocks.dto.stock_record_model_dto import (QueryRequestModelDTO,
                                                   StockRecordQueryResponseModelDTO)


class StockRecordDAO:

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_new_stock_record(self, product_id):
        await self.session.begin_nested()
        self.session.add(StockRecordModel(product_id=product_id,
                                          change_datetime=func.now(),
                                          quantity_actual=0,
                                          quantity_before=0,
                                          quantity_change=0,
                                          quantity_change_direction=0,
                                          change_source_id=None
                                          ))

        try:
            await self.session.commit()
        except exc.IntegrityError as e:
            if "asyncpg.exceptions.UniqueViolationError" not in e.args[0] \
                or "product_id__change_source_id_uniqe" not in e.args[0]:
                raise
            logger.warning('Duplicate stock record insertion skipped. Product id: {}',
                           product_id)
            await self.session.rollback()

    async def create_incoming_stock_record(self, document: Document):

        try:
            await self.session.begin_nested()

            await self.session.execute(
                insert(DocumentStatusRecordModel).values(document_id=document.id,
                                                         status=DocumentStatus.PROCESSING,
                                                         created=func.now(),
                                                         updated=func.now()))

            union_selects = []
            for i, item in enumerate(document.items):
                quantity_actual_select = \
                    select([bindparam(f'{i}-new_stock_record_id', value=uuid.uuid4(),
                                      type_=UUID(as_uuid=True)),
                            StockRecordModel.product_id,
                            bindparam('document_id', type_=String()),
                            bindparam(f'{i}-item_quantity', value=item.quantity,
                                      type_=Float()),
                            bindparam("document_direction",
                                      type_=Integer()),
                            StockRecordModel.quantity_actual,
                            StockRecordModel.quantity_actual + bindparam(
                                f'{i}-directional_quantity',
                                item.quantity * document.direction,
                                type_=Float()),
                            func.now(),
                            StockRecordModel.stock_record_id]) \
                        .where(
                        StockRecordModel.product_id == bindparam(
                            f'{i}-product_id_param',
                            item.product_id,
                            type_=String())) \
                        .order_by(StockRecordModel.change_datetime.desc()).limit(
                        1)
                union_selects.append(quantity_actual_select)

            query = union(*tuple(union_selects))
            insert_sql = insert(StockRecordModel).from_select(
                ['stock_record_id',
                 'product_id',
                 'change_source_id',
                 'quantity_change',
                 'quantity_change_direction',
                 'quantity_before',
                 'quantity_actual',
                 'change_datetime',
                 'previous_stock_record_id'], query)

            await self.session.execute(insert_sql, [{'document_direction': document.direction,
                                                     'document_id': document.id}])

            sql = select(func.count(StockRecordModel.stock_record_id)).where((StockRecordModel.change_source_id == document.id))
            res = await self.session.execute(sql, [{}])
            count = res.scalar_one()
            if count < len(document.items):
                await self.session.rollback()
                await self.session.execute(
                    insert(DocumentStatusRecordModel).values(
                        document_id=document.id,
                        status=DocumentStatus.UNKNOWN_ITEMS,
                        created=func.now(),
                        updated=func.now()))
                await self.session.commit()
                return True


            if document.validate_stock_availability and document.direction < 0:
                sql = select(func.count(StockRecordModel.stock_record_id)).where((StockRecordModel.change_source_id == document.id) & (StockRecordModel.quantity_actual < 0))
                res = await self.session.execute(sql, [{}])
                count = res.scalar_one()
                if count > 0:
                    await self.session.rollback()
                    await self.session.execute(
                        insert(DocumentStatusRecordModel).values(
                            document_id=document.id,
                            status=DocumentStatus.INSUFFICIENT_STOCK,
                            created=func.now(),
                            updated=func.now()))
                    await self.session.commit()
                    return True




            await self.session.execute(update(DocumentStatusRecordModel).where(
                DocumentStatusRecordModel.document_id == document.id).values(
                status=DocumentStatus.ACCEPTED))

            await self.session.commit()

            return True

        except exc.IntegrityError as e:
            await self.session.rollback()
            if "asyncpg.exceptions.UniqueViolationError" not in e.args[0] \
                    or "product_id__change_source_id_uniqe" not in e.args[0]:
                return False
            logger.warning('Duplicate document skipped: {}', e)
            return True
        except Exception:
            raise

    async def get_document_status_record(self,
                                         document_id: str) -> DocumentStatusRecordModel:
        return await self.session.get(DocumentStatusRecordModel, document_id)

    async def set_document_status_record(self, document_id: str,
                                         status: str):
        await self.session.execute(
            insert(DocumentStatusRecordModel(document_id=document_id,
                                             status=status,
                                             created=func.now(),
                                             updated=func.now())))

    async def query_stock_records_for_product(self, product_id: str,
                                              request: QueryRequestModelDTO) -> StockRecordQueryResponseModelDTO:

        order = StockRecordModel.change_datetime.desc()
        if request.sortField in ["stock_record_id", "product_id", "change_source_id",
                                 "quantity_change", "quantity_change_direction",
                                 "quantity_before", "quantity_actual",
                                 "change_datetime"] and request.sortOrder != 0:
            order = (getattr(StockRecordModel,
                             request.sortField).asc()) if request.sortOrder > 0 else (
                getattr(StockRecordModel, request.sortField).desc())

        raw_stock_records = await self.session.execute(
            select(StockRecordModel)
            .where(StockRecordModel.product_id == product_id)
            .limit(request.rows)
            .offset(request.offset)
            .order_by(order)
        )

        total_rec_count = (await self.session.execute(
            select(func.count(StockRecordModel.stock_record_id)).where(
                StockRecordModel.product_id == product_id))).scalar_one()
        current_requested_page = int(request.offset / request.rows)
        total_pages_count = int(total_rec_count / request.rows)
        page = (current_requested_page + 1) if (
            current_requested_page < int(total_rec_count / request.rows)) else int(
            total_rec_count / request.rows) + 1

        response = StockRecordQueryResponseModelDTO.construct(
            result=raw_stock_records.scalars().fetchall(),
            total_records_count=total_rec_count,
            total_pages_count=total_pages_count,
            page=page,
            records_per_page_count=request.rows,
            is_prev=page > 1,
            is_next=page < total_pages_count
        )

        return response

from fastapi import Body, APIRouter
from fastapi.param_functions import Depends

from msrdstocks.db.dao.stock_record_dao import StockRecordDAO
from msrdstocks.dto.stock_record_model_dto import (StockRecordQueryResponseModelDTO,
                                                   QueryRequestModelDTO)

router = APIRouter()


@router.post("/query", response_model=StockRecordQueryResponseModelDTO)
async def query_stock_records_for_product(
    product_id: str,
    request: QueryRequestModelDTO = Body(),
    stock_record_dao: StockRecordDAO = Depends(),
) -> StockRecordQueryResponseModelDTO:
    return await stock_record_dao.query_stock_records_for_product(product_id, request)

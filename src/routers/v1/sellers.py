from typing import Annotated

from fastapi import APIRouter, Depends, status, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.configurations.database import get_async_session
from src.schemas.sellers import BaseSeller, IncomingSeller, ReturnedSeller, ReturnedAllSellers, ReturnedSellerWithBooks
from src.services.sellers import SellerService

sellers_router = APIRouter(prefix="/seller", tags=["sellers"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: IncomingSeller, session: DBSession):
    try:
        new_seller = await SellerService(session).add_seller(seller)
        return new_seller
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Продавец с таким email уже существует."
        )

@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    sellers = await SellerService(session).get_all_sellers()
    return {"sellers": sellers}

@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_single_seller(seller_id: int, session: DBSession):
    seller = await SellerService(session).get_single_seller(seller_id)

    if seller is not None:
        return seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)

@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, seller_data: BaseSeller, session: DBSession):
    try:
        updated_seller = await SellerService(session).update_seller(seller_id, seller_data)
        if updated_seller is not None:
            return updated_seller
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой email уже используется другим продавцом."
        )


@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted = await SellerService(session).delete_seller(seller_id)

    if deleted:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return Response(status_code=status.HTTP_404_NOT_FOUND)
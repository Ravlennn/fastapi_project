__all__ = ["SellerService"]

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sellers import Seller
from src.schemas.sellers import BaseSeller, IncomingSeller, ReturnedSeller

class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_seller(self, seller: IncomingSeller) -> Seller:
        new_seller = Seller(
            **{
                "first_name": seller.first_name,
                "last_name": seller.last_name,
                "e_mail": seller.e_mail,
                "password": seller.password,
            }
        )

        self.session.add(new_seller)
        await self.session.flush()

        return new_seller

    async def get_all_sellers(self) -> list[Seller]:
        query = select(Seller)
        result = await self.session.execute(query)
        
        return result.scalars().all()

    async def get_single_seller(self, seller_id: int) -> Seller | None:
        query = select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
        result = await self.session.execute(query)
        
        return result.scalars().first()

    async def delete_seller(self, seller_id: int) -> bool:
        if seller := await self.session.get(Seller, seller_id):
            await self.session.delete(seller)
            await self.session.flush()
            return True

        return False

    async def update_seller(self, seller_id: int, new_seller_data: BaseSeller) -> Seller | None:
        if updated_seller := await self.session.get(Seller, seller_id):
            updated_seller.first_name = new_seller_data.first_name
            updated_seller.last_name = new_seller_data.last_name
            updated_seller.e_mail = new_seller_data.e_mail

            await self.session.flush()

            return updated_seller
            
        return None
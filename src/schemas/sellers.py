from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

from src.schemas.books import ReturnedBook

__all__ = [
    "BaseSeller",
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedAllSellers",
     "ReturnedSellerWithBooks",

]

class BaseSeller(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    e_mail: str = Field(max_length=50)

class IncomingSeller(BaseSeller):
    password: str = Field(max_length=100)

    @field_validator("password")
    @staticmethod
    def validate_password(val: str):
        if len(val) < 8:
            raise PydanticCustomError("Validation error", "Password must be at least 8 characters long!")
        if val.isdigit():
            raise PydanticCustomError("Validation error", "Password cannot contain only digits!")
        return val
    
    @field_validator("first_name", "last_name")
    @staticmethod
    def validate_names(val: str):
        if not val.strip():
            raise PydanticCustomError("Validation error", "Name fields cannot be empty!")
        return val

class ReturnedSeller(BaseSeller):
    id: int

class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]

class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook] = []

import pytest
from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller

API_V1_URL_PREFIX = "/api/v1/seller"

@pytest.mark.asyncio()
async def test_create_seller(async_client):
    data = {
        "first_name": "Pavel",
        "last_name": "Kholkin",
        "e_mail": "p.kholkin@g.nsu.ru",
        "password": "zxcmagicdemon777"
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    result_data = response.json()
    
    assert "password" not in result_data
    
    resp_id = result_data.pop("id", None)
    assert resp_id is not None

    assert result_data == {
        "first_name": "Pavel",
        "last_name": "Kholkin",
        "e_mail": "p.kholkin@g.nsu.ru"
    }

@pytest.mark.asyncio()
async def test_create_seller_duplicate_email(db_session, async_client):
    seller = Seller(first_name="Test", last_name="User", e_mail="test@mail.ru", password="123")
    db_session.add(seller)
    await db_session.flush()

    data = {
        "first_name": "Clone",
        "last_name": "Clone",
        "e_mail": "test@mail.ru",
        "password": "password123456"
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio()
async def test_get_all_sellers(db_session, async_client):
    seller1 = Seller(first_name="A", last_name="B", e_mail="a@b.com", password="1")
    seller2 = Seller(first_name="C", last_name="D", e_mail="c@d.com", password="2")
    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["sellers"]) == 2

@pytest.mark.asyncio()
async def test_get_single_seller_with_books(db_session, async_client):
    seller = Seller(first_name="Author", last_name="Writer", e_mail="auth@mail.ru", password="123")
    db_session.add(seller)
    await db_session.flush()

    book = Book(title="My Book", author="Author", year=2026, pages=100, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{seller.id}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["first_name"] == "Author"
    assert "password" not in data
    assert len(data["books"]) == 1
    assert data["books"][0]["title"] == "My Book"

@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    seller = Seller(first_name="Old", last_name="Name", e_mail="old@mail.ru", password="123")
    db_session.add(seller)
    await db_session.flush()

    update_data = {
        "first_name": "New",
        "last_name": "Name",
        "e_mail": "new@mail.ru"
    }
    
    response = await async_client.put(f"{API_V1_URL_PREFIX}/{seller.id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    
    updated_seller = await db_session.get(Seller, seller.id)
    assert updated_seller.first_name == "New"
    assert updated_seller.e_mail == "new@mail.ru"

@pytest.mark.asyncio()
async def test_delete_seller_cascade_books(db_session, async_client):
    seller = Seller(first_name="Delete", last_name="Me", e_mail="del@mail.ru", password="password123")
    db_session.add(seller)
    await db_session.flush()

    book = Book(title="title", author="author", year=2026, pages=10, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    deleted_seller = await db_session.get(Seller, seller.id)
    assert deleted_seller is None

    deleted_book = await db_session.get(Book, book.id)
    assert deleted_book is None

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.books import Book, fake_storage
from src.schemas import IncomingBook, PatchBook, ReturnedAllBooks, ReturnedBook

books_router = APIRouter(prefix="/books", tags=["books", "v1"])


DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка, возвращающая все книги
@books_router.get("/", response_model=ReturnedAllBooks)
async def get_all_books(session: DBSession):
    # Хотим видеть формат
    # books: [{"id": 1, "title": "blabla", ...., "year": 2023},{...}]

    query = select(Book)  # SELECT * FROM boocs_table;
    result = await session.execute(query)  # await session.execute(select(Book))

    books = result.scalars().all()
    return {"books": books}


# Ручка для создания записи о книге в БД. Возвращает созданную книгу.
@books_router.post("/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)
async def create_book(book: IncomingBook, session: DBSession):  # прописываем модель валидирующую входные данные
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_book = Book(
        **{
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "pages": book.pages,
        }
    )

    session.add(new_book)
    await session.flush()

    # return ORJSONResponse({"book": new_book}, status_code=status.HTTP_201_CREATED) # Альтернатива для возврата кода
    return new_book


# Ручка для получения книги по ее ИД
@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_single_book(book_id: int, session: DBSession):
    book = fake_storage.get(book_id)

    if book is not None:
        return book

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления книги
@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    deleted_book = fake_storage.pop(book_id, None)
    if deleted_book is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о книге
@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book_data: ReturnedBook):
    # book = fake_storage.get(book_id, None)
    # if book:
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его. Заменяет то, что закомментировано выше.
    if _ := fake_storage.get(book_id):
        new_book = {
            "id": book_id,
            "title": new_book_data.title,
            "author": new_book_data.author,
            "year": new_book_data.year,
            "pages": new_book_data.pages,
        }

        fake_storage[book_id] = new_book

    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return fake_storage[book_id]


# Ручка для частичного обновления данных о книге
@books_router.patch("/{book_id}", response_model=ReturnedBook)
async def patch_book(book_id: int, patched_book: PatchBook):
    if book := fake_storage.get(book_id):

        if patched_book.title is not None and patched_book.title != book["title"]:
            book["title"] = patched_book.title
        if patched_book.author is not None and patched_book.author != book["author"]:
            book["author"] = patched_book.author
        if patched_book.year is not None and patched_book.year != book["year"]:
            book["year"] = patched_book.year
        if patched_book.pages is not None and patched_book.pages != book["pages"]:
            book["pages"] = patched_book.pages

        fake_storage[book_id] = book

    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return fake_storage[book_id]

from fastapi import FastAPI, HTTPException, Request, Form
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, Session
from pydantic import BaseModel, ConfigDict
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI()

engine = create_engine('postgresql+psycopg2://postgres:Artul251220@localhost:5432/postgres')
templates = Jinja2Templates(directory="templates_books")


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books1"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(default="Автор")
    year: Mapped[int] = mapped_column(default=2026)
    is_read: Mapped[bool] = mapped_column(default=False)


Base.metadata.create_all(bind=engine)


class BookCreate(BaseModel):
    title: str
    author: str
    year: int


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    year: int | None = None
    is_read: bool | None = None


class BookRead(BaseModel):
    id: int
    title: str
    author: str
    year: int
    is_read: bool
    model_config = ConfigDict(from_attributes=True)


@app.get("/books/read", response_model=list[BookRead])
def get_read_books():
    with Session(engine) as session:
        query = select(Book).where(Book.is_read.is_(True))
        books = session.scalars(query).all()
        return books


@app.get("/books/unread", response_model=list[BookRead])
def get_unread_books():
    with Session(engine) as session:
        query = select(Book).where(Book.is_read == False)
        books = session.scalars(query).all()
        return books


@app.get("/books/", response_model=list[BookRead])
def get_all_books():
    with Session(engine) as session:
        query = select(Book)
        books = session.scalars(query).all()
        return books


@app.get("/books/{book_id}", response_model=BookRead)
def get_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        return book


@app.post("/books/", response_model=BookRead)
def create_book(book: BookCreate):
    with Session(engine) as session:
        book = Book(title=book.title, author=book.author, year=book.year)
        session.add(book)
        session.commit()
        session.refresh(book)
        return book


@app.patch("/books/{book_id}", response_model=BookRead)
def update_book(book_id: int, new_book_data: BookUpdate):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="book not found")
        update_data = new_book_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(book, field, value)
        session.commit()
        session.refresh(book)
        return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        session.delete(book)
        session.commit()
        return {"message": "Book deleted"}


@app.patch("/books/{book_id}/read", response_model=BookRead)
def toggle_book(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        book.is_read = not book.is_read
        session.commit()
        session.refresh(book)
        return book


@app.get("/pages/books")
def list_pages(request: Request):
    with Session(engine) as session:
        query = select(Book)
        books = session.scalars(query).all()
        book_data = []
        for book in books:
            book_data.append(
                {"id": book.id, "title": book.title, "author": "Автор", "year": "Год", "is_read": book.is_read}
            )

        return templates.TemplateResponse(request, "books.html", {"request": request, "books": book_data})


@app.get("/pages/books/add")
def add_book_page(request: Request):
    return templates.TemplateResponse(request, "add_book.html", {"request": request})


@app.post("/pages/books/add", response_model=BookRead)
def add_book_from_form(title: str = Form(...)):
    with Session(engine) as session:
        book = Book(title=title)
        session.add(book)
        session.commit()
        return RedirectResponse(url="/pages/books", status_code=303)


@app.get("/pages/books/{book_id}/edit")
def edit_book_page(request: Request, book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        book_data = {"id": book.id, "title": book.title, "is_read": book.is_read}
    return templates.TemplateResponse(request, "book_edit.html", {"request": request, "book": book_data})


@app.post("/pages/books/{book_id}/edit", response_model=BookRead)
def edit_book_from_form(book_id: int, title: str = Form(...), is_read: bool = Form(False)):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        book.title = title
        book.is_read = is_read
        session.commit()
        session.refresh(book)
    return RedirectResponse(url="/pages/books", status_code=303)


@app.post("/pages/books/{book_id}/delete")
def delete_book_page(book_id: int):
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        session.delete(book)
        session.commit()
    return RedirectResponse(url="/pages/books", status_code=303)
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from sqlalchemy.sql import func

app = FastAPI()

# Настройка базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Record(Base):
    """
    Класс Record создает модель для хранения записей.

    С атрибутами:
        id (int): Уникальный идентификатор записи.
        title (str): Заголовок записи.
        description (str): Описание записи.
        created_at (datetime): Дата и время создания записи.
    """
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())


# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Инициализация шаблонов Jinja2
templates = Jinja2Templates(directory="templates")


class RecordCreate(BaseModel):
    """
    Класс RecordCreate для проверки валидации данных при создании записи.

    С атрибутами:
        title (str): Заголовок записи.
        description (str): Описание записи.
    """
    title: str
    description: str


@app.get("/", response_class=HTMLResponse)
def read_records(request: Request):
    """
    Функций для отображения всех записей.

    С атрибутами:
        request (Request): Объект запроса FastAPI.
    Возвращает:
        TemplateResponse: HTML-страница со списком записей.
        """
    session = SessionLocal()
    records = session.query(Record).all()
    return templates.TemplateResponse("record_list.html", {"request": request, "records": records})


@app.get("/add/", response_class=HTMLResponse)
def add_record_form(request: Request):
    """
    Функция для отображения формы добавления записи.

    С атрибутами:
        request (Request): Объект запроса FastAPI.
    Возвращает:
        TemplateResponse: HTML-страница с формой для добавления записи.

    """
    return templates.TemplateResponse("add_record.html", {"request": request})


@app.post("/add/")
def add_record(title: str = Form(...), description: str = Form(...)):
    """
    Функция для добавления новой записи.

    С атрибутами:
        title (str): Заголовок новой записи.
        description (str): Описание новой записи.
    Возвращает:
        RedirectResponse: Перенаправление на страницу со списком записей.
    """
    session = SessionLocal()
    new_record = Record(title=title, description=description)
    session.add(new_record)
    session.commit()
    return RedirectResponse("/", status_code=303)


@app.get("/delete/{record_id}", response_class=HTMLResponse)
def delete_record(record_id: int):
    """
    Функция для удаления записи.

    С атрибутами:
        record_id (int): Уникальный идентификатор записи.
    С исключением:
        HTTPException: Если запись не найдена.
    Возвращает:
        RedirectResponse: Перенаправление на страницу со списком записей.
    """
    session = SessionLocal()
    record = session.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    session.delete(record)
    session.commit()
    return RedirectResponse("/", status_code=303)

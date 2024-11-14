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


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())


Base.metadata.create_all(bind=engine)


templates = Jinja2Templates(directory="templates")


class RecordCreate(BaseModel):
    title: str
    description: str


@app.get("/", response_class=HTMLResponse)
def read_records(request: Request):
    session = SessionLocal()
    records = session.query(Record).all()
    return templates.TemplateResponse("record_list.html", {"request": request, "records": records})


@app.get("/add/", response_class=HTMLResponse)
def add_record_form(request: Request):
    return templates.TemplateResponse("add_record.html", {"request": request})


@app.post("/add/")
def add_record(title: str = Form(...), description: str = Form(...)):
    session = SessionLocal()
    new_record = Record(title=title, description=description)
    session.add(new_record)
    session.commit()
    return RedirectResponse("/", status_code=303)


@app.get("/delete/{record_id}", response_class=HTMLResponse)
def delete_record(record_id: int):
    session = SessionLocal()
    record = session.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    session.delete(record)
    session.commit()
    return RedirectResponse("/", status_code=303)

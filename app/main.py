from fastapi import FastAPI, Depends
from database import engine, SessionLocal
import models
from typing import Annotated
from sqlalchemy.orm import Session

app = FastAPI()


models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_injection = Annotated[Session, Depends(get_db)]


@app.get("/todo")
async def test(db: db_injection):
    todos = db.query(models.Todos).all()
    return todos

from fastapi import FastAPI, Depends, HTTPException, status
import models
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos, TodosBodyRequest

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/todos/", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency):
    todo = db.query(Todos).all()
    if todo:
        return todo
    raise HTTPException(
        {"error": "no todos"},
        status_code=status.HTTP_404_NOTFOUND
    )


@app.get("/todos/{id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(id: int, db: db_dependency):
    todo = db.query(Todos).filter(Todos.id == id).first()
    if todo:
        return todo
    raise HTTPException(
        {"error": "there is no todo with ids"},
        status_code=status.HTTP_404_NOT_FOUND
    )


@app.post("/create-todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(data: TodosBodyRequest, db: db_dependency):
    new_todo = Todos(**data.dict())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    if new_todo.id:
        return new_todo
    raise HTTPException(
        {"details": "there is error in creation "},
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@app.put("/update-todo/{id}", status_code=status.HTTP_201_CREATED)
async def update_todo(id: int, data: TodosBodyRequest, db: db_dependency):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail=" Todo not found.")
    todo_model.title = data.title
    todo_model.description = data.description
    todo_model.priority = data.priority
    todo_model.complete = data.complete
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    if todo_model.id:
        return todo_model
    raise HTTPException(
        {"details": "there is error in creation "},
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@app.delete("/delete-todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(id: int, db: db_dependency):
    todo = db.get(Todos, id)
    db.delete(todo)
    db.commit()

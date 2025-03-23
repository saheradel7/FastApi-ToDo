from fastapi import APIRouter, status, HTTPException, Path, Depends
from pydantic import BaseModel, Field
from database import engine
from todos.models import Todos
import todos.models as todos_models
from database import db_injection
from accounts.auth import get_current_user
from typing import Annotated

router = APIRouter(prefix="/todo", tags=["todo"])


todos_models.Base.metadata.create_all(bind=engine)

user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequestFormat(BaseModel):
    title: str = Field(min_length=3)
    description: str
    priority: int
    completed: bool


@router.get("", status_code=status.HTTP_200_OK)
async def all_todos(db: db_injection):
    todos = db.query(Todos).all()
    return todos


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def todo_details(db: db_injection, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_injection, data: TodoRequestFormat):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, details="failed to authorize"
        )

    todo = Todos(**data.dict(), owner_id=user.get("id"))
    db.add(todo)
    db.commit()
    db.refresh(todo)
    if todo.id:
        return todo

    raise HTTPException(status_code=status.HTTP_401_BAD_REQUEST)


@router.put("/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(
    db: db_injection, data: TodoRequestFormat, todo_id: int = Path(gt=0)
):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    todo.title = data.title
    todo.description = data.description
    todo.priority = data.priority
    todo.completed = data.completed

    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_injection, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    db.delete(todo)
    db.commit()
    return

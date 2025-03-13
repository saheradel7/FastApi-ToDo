from database import Base
from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel, Field


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)


class TodosBodyRequest(BaseModel):
    title: str = Field(min_length=5)
    description: str = Field(min_length=5)
    priority: int = Field(gt=0)
    complete: bool

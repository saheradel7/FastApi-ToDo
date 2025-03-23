from fastapi import FastAPI
from database import engine, SessionLocal
from accounts import auth
from todos import todos

app = FastAPI()

app.include_router(auth.router)
app.include_router(todos.router)

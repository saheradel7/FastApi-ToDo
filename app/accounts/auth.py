from fastapi import APIRouter, status, HTTPException, Path, Depends
import accounts.models as auth_models
from pydantic import BaseModel, Field
from database import engine
from database import db_injection
from accounts.models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone

router = APIRouter(prefix="/auth", tags=["auth"])
auth_models.Base.metadata.create_all(bind=engine)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = "secretkey123456789"
ALGORITHM = "HS256"


async def get_current_user(token: Annotated[str, Depends(auth2_bearer)]):
    print(f"Received Token: '{token}'")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        id: int = payload.get("id")
        if username is None or id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="could not validate user 1",
            )
        return {"username": username, "id": id}
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user 2"
        )


class UserBodyRequestForm(BaseModel):
    email: str = Field(max_length=50)
    username: str = Field(max_length=50)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    hashed_password: str
    is_active: bool
    role: str = Field(max_length=50)


@router.get("", status_code=status.HTTP_200_OK)
async def all_users(db: db_injection):
    return db.query(Users).all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_injection, data: UserBodyRequestForm):
    user = Users(
        email=data.email,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=bcrypt_context.hash(data.hashed_password),
        is_active=data.is_active,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", status_code=status.HTTP_200_OK)
def login(data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_injection):
    user = db.query(Users).filter(Users.username == data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not bcrypt_context.verify(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    encode = {"sub": user.username, "id": user.id}
    expires = datetime.now(timezone.utc) + timedelta(minutes=20)
    encode.update({"exp": expires})
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import uuid
import jwt
import bcrypt
from typing import Optional

from src.app.database import get_db
from src.app.models import User, Profile, UserSettings
from src.app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# Use secret key from settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

MIN_PASSWORD_LENGTH = 8


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Store emails in lowercase to prevent duplicate case variants."""
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
            )
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


def verify_password(plain_password, hashed_password):
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def get_password_hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_data.password)
    user_id = str(uuid.uuid4())

    new_user = User(
        id=user_id,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    db.refresh(new_user)

    # Generate token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "uid": new_user.id}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": new_user.id, "email": new_user.email}
    }


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact support for assistance.",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email, "uid": db_user.id}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": db_user.id, "email": db_user.email}
    }

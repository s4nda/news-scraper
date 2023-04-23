from utils.db import get_db_client
from pydantic import BaseModel, Field, validator
from argon2 import PasswordHasher
from utils.exceptions import (
    ResourceAlreadyExists,
    ResourceNotFound,
    InvalidToken,
    NotAuthorized,
)
import time
import uuid
from config import Config
import jwt

db = get_db_client()
ph = PasswordHasher()


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str | None
    email: str
    password: str = Field(min_length=6, max_length=256)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    reset_password_token: str | None

    @validator("email")
    def validate_email(cls, value):
        if "@" not in value:
            raise ValueError("Not a valid email address")
        return value.lower()

    @validator("password")
    def validate_password(cls, value):
        hashed = ph.hash(value)
        return hashed


class UserLogin(BaseModel):
    access_token: str
    user: User


class UsersModel:
    def create(self, user: User) -> User:
        found_user = db.users.find_one({"email": user.email})
        if found_user:
            raise ResourceAlreadyExists("User already exists")
        user_dict = user.dict()
        db.users.insert_one(user_dict)
        created_user = db.users.find_one({"id": user.id})
        return User.parse_obj(created_user)

    def delete(self, user: User) -> None:
        db.users.delete_one({"id": user.id})

    def get(self, user_id) -> User:
        found_by_id = db.users.find_one({"id": user_id})
        if not found_by_id:
            raise ResourceNotFound("User not found")
        return User.parse_obj(found_by_id)

    def make_access_token(self, user: User) -> str:
        expires_at = time.time() + Config.jwt_expires_after_seconds
        access_token = jwt.encode(
            {"id": user.id, "email": user.email, "exp": expires_at},
            Config.jwt_secret_key,
        )
        return access_token

    def login(self, email, password) -> UserLogin:
        found_user = db.users.find_one({"email": email})
        if not found_user:
            raise NotAuthorized("Bad Login")
        hashed = found_user.get("password", "")
        ph.verify(hashed, password)
        user = User.parse_obj(found_user)
        return UserLogin.parse_obj(
            {"user": user, "access_token": self.make_access_token(user)}
        )

    def request_password_reset_token(self, email):
        found_user = db.users.find_one({"email": email})
        if not found_user:
            raise ResourceNotFound("User does not exsit")
        token = str(uuid.uuid4())[:5].upper()
        db.users.update_one({"email": email}, {"$set": {"password_reset_token": token}})
        return found_user["password_reset_token"]

    def reset_password(self, email, token, new_password):
        found_by_token = db.users.find_one({"password_reset_token": token})
        if not found_by_token:
            raise InvalidToken("Invalid Token")
        if found_by_token and found_by_token.get(email) == email:
            db.users.update_one(
                {"email": email},
                {
                    "$set": {
                        "password_reset_token": None,
                        "password": new_password,
                        "updated_at": time.time,
                    }
                },
            )
        updated = db.users.find_one({"id": found_by_token["id"]})
        return User.parse_obj(updated)

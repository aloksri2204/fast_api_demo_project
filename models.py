from typing import List

from pydantic import BaseModel, Field


class Products(BaseModel):
    id: int
    name: str
    desc: str
    price: float
    quantity: int


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    permissions: List[str]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=1, max_length=100)
    role: str

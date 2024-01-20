# user base schemas
from pydantic import BaseModel
from models import UserRoles
from typing import List
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    role: UserRoles = UserRoles.user


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str


# place base schemas
class PlaceBase(BaseModel):
    title: str
    content: str
    tags: List[str]
    user_id: int
    user_full_name: str
    rating_score: float


class PlaceCreate(PlaceBase):
    pass


# Place response schema
class PlaceResponse(BaseModel):
    id: int
    img: str  # Change the type to str for URLs
    title: str
    content: str
    tags: List[str]
    user_id: int
    user_full_name: str
    rating_score: float
    posted_date: datetime

    class Config:
        orm_mode = True


class PlaceGetByUserId(BaseModel):
    user_id: int


class PlaceGetByPlaceId(BaseModel):
    place_id: int


class PlaceGetByTag(BaseModel):
    tag: str


# Add a new schema for creating a comment
class CommentBase(BaseModel):
    comment_text: str
    email: str
    name: str


class CommentCreate(CommentBase):
    place_id: int
    user_id: int


class CommentByUserIdResponse(BaseModel):
    comment_id: int
    comment_text: str
    email: str
    name: str
    commented_at: datetime
    user_id: int
    place_id: int


class CommentByPlaceIdResponse(BaseModel):
    comment_id: int
    comment_text: str
    email: str
    name: str
    commented_at: datetime
    user_id: int
    place_id: int


class CreatePlaceComment(BaseModel):
    place_id: int


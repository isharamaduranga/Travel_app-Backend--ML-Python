# user base schemas
from fastapi import UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    user_img: Optional[UploadFile] = Form(None)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    user_img: Optional[UploadFile] = None


class User(UserBase):
    id: int
    user_img: str

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


class PlaceResponseWithImg(BaseModel):
    id: int
    img: str  # Existing img field
    user_img: str  # New user_img field
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


class CommentResponse(BaseModel):
    comment_id: int
    comment_text: str
    email: str
    name: str
    commented_at: datetime
    user_id: int
    user_image: str
    place_id: int


class PlaceWithCommentsResponse(BaseModel):
    id: int
    img: str
    title: str
    content: str
    tags: List[str]
    user_id: int
    user_full_name: str
    rating_score: float
    posted_date: datetime
    comments: List[CommentResponse]

    class Config:
        orm_mode = True

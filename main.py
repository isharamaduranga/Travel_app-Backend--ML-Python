import os
from typing import List

from fastapi import Depends, FastAPI, File, Form, HTTPException
from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from crud import create_user, get_user, get_users, authenticate_user, delete_user_from_db, create_place, get_all_places, \
    get_places_by_user_id, get_place_by_place_id, get_places_by_tag, create_comment, get_comments_by_user_id, \
    get_comments_by_place_id
from database import SessionLocal, engine
from ml_model import predict_score, TransformersPipelineException
from models import Base
from response_models import create_response
from schemas import UserCreate, User, UserLogin, PlaceCreate, PlaceResponse, PlaceGetByPlaceId, \
    CommentCreate, PlaceGetByUserId, CommentByUserIdResponse, CommentByPlaceIdResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing) for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get the current user from the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API to register a new user
@app.post("/api/v1/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return create_user(db, **user.dict())
    except IntegrityError as e:
        # Handle unique constraint violation (email already exists)
        return create_response("error", "Email already registered !", data=None)


# API to login
@app.post("/api/v1/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, username=user_credentials.username, password=user_credentials.password)
    if user:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
        return create_response("success", "Successfully login", data=user_data)
    else:
        return create_response("error", "Invalid Credential!", data=None)


# API to get all users
@app.get("/api/v1/users", response_model=list[User])
def get_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)


# API to get a specific user
@app.get("/api/v1/users/{user_id}")
def get_specific_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = get_user(db, user_id)
        if user is not None:
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
            return create_response("success", "User retrieved successfully", data=user_data)
        else:
            return create_response("error", "User not found", data=None)
    except Exception as e:
        return create_response("error", f"Internal Server Error: {str(e)}", data=None)


@app.delete("/api/v1/users/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    try:
        deleted_user = delete_user_from_db(db, user_id)
        if deleted_user:
            return create_response("success", "User deleted successfully", data=None)
        else:
            return create_response("error", "User not found", data=None)
    except Exception as e:
        return create_response("error", f"Internal Server Error: {str(e)}", data=None)


# API to create a new place
@app.post("/api/v1/createPlace/")
def create_place_endpoint(
        title: str = Form(...),
        content: str = Form(...),
        tags: str = Form(...),
        user_id: int = Form(...),
        user_full_name: str = Form(...),
        rating_score: float = Form(...),
        img: UploadFile = File(...),
        db: Session = Depends(get_db),
):
    try:
        # Ensure 'uploads' directory exists
        os.makedirs("uploads", exist_ok=True)

        # Save the uploaded image to a temporary file
        temp_file_path = f"uploads/{img.filename}"

        # Print debug information
        print(f"Temp file path: {temp_file_path}")

        with open(temp_file_path, "wb") as f:
            f.write(img.file.read())

        # Create a new PlaceCreate object
        place_data = PlaceCreate(
            title=title,
            content=content,
            tags=tags.split(','),  # Assuming tags are comma-separated
            user_id=user_id,
            user_full_name=user_full_name,
            rating_score=rating_score,
        )

        # Create the place in the database
        new_place = create_place(db, place_data, img)

        place = {
            "place_id": new_place.id,
            "user_id": new_place.user_id
        }

        return create_response("success", "Place created successfully", data=place)

    except IntegrityError as e:
        db.rollback()
        return create_response("error", f"Internal Server Error: {str(e)}", data=None)
        # raise HTTPException(status_code=400, detail=f"Error creating place: {str(e)}")

    except Exception as e:
        db.rollback()
        return create_response("error", f"Internal Server Error: {str(e)}", data=None)
        # raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# API to get all places
@app.get("/api/v1/places", response_model=List[PlaceResponse])
def get_all_places_endpoint(db: Session = Depends(get_db)):
    places = get_all_places(db)

    # Convert tags from comma-separated string to list
    for place in places:
        place.tags = place.tags.split(',')

    return places


# API to get places by user ID
@app.post("/api/v1/places/getByUserId", response_model=List[PlaceResponse])
def get_places_by_user_id_endpoint(user_data: PlaceGetByUserId, db: Session = Depends(get_db)):
    places = get_places_by_user_id(db, user_id=user_data.user_id)

    # Convert tags from comma-separated string to list
    for place in places:
        place.tags = place.tags.split(',')

    return places


# API to get a place by place ID
@app.post("/api/v1/places/getByPlaceId", response_model=PlaceResponse)
def get_place_by_place_id_endpoint(place_data: PlaceGetByPlaceId, db: Session = Depends(get_db)):
    place = get_place_by_place_id(db, place_id=place_data.place_id)

    # Convert tags from comma-separated string to list
    if place:
        place.tags = place.tags.split(',')

    return place


# API to get places by tag
@app.get("/api/v1/places/getByCategory/{tag}", response_model=List[PlaceResponse])
def get_places_by_tag_endpoint(tag: str, db: Session = Depends(get_db)):
    places = get_places_by_tag(db, tag=tag)

    # Convert tags from comma-separated string to list
    for place in places:
        place.tags = place.tags.split(',')

    return places


# Api to create new comment related place
@app.post("/api/v1/createComment")
def create_comment_endpoint(comment: CommentCreate, db: Session = Depends(get_db)):
    try:
        new_comment = create_comment(db, comment)
        return create_response("success", "Comment created successfully", data={"comment_id": new_comment.id})
    except Exception as e:
        return create_response("error", f"Internal Server Error: {str(e)}", data=None)


@app.get("/api/v1/getCommentsByUserId/{user_id}", response_model=List[CommentByUserIdResponse])
def get_comments_by_user_id_endpoint(user_id: int, db: Session = Depends(get_db)):
    comments = get_comments_by_user_id(db, user_id)

    # Map the results to CommentByUserIdResponse
    comments_response = [
        CommentByUserIdResponse(
            comment_id=comment.id,
            comment_text=comment.comment_text,
            email=comment.email,
            name=comment.name,
            commented_at=comment.commented_at,
            user_id=comment.user_id,
            place_id=comment.place_id
        )
        for comment in comments
    ]

    return comments_response


@app.get("/api/v1/getCommentsByPlaceId/{place_id}", response_model=List[CommentByPlaceIdResponse])
def get_comments_by_place_id_endpoint(place_id: int, db: Session = Depends(get_db)):
    comments = get_comments_by_place_id(db, place_id)
    # Map the results to CommentByUserIdResponse
    comments_response = [
        CommentByUserIdResponse(
            comment_id=comment.id,
            comment_text=comment.comment_text,
            email=comment.email,
            name=comment.name,
            commented_at=comment.commented_at,
            user_id=comment.user_id,
            place_id=comment.place_id
        )
        for comment in comments
    ]

    return comments_response


def create_response(status, message, data):
    return {"status": status, "message": message, "data": data}


@app.post("/api/v1/places/scoreAndUpdate/{place_id}")
def score_and_update_place(
        place_id: int, db: Session = Depends(get_db)
):
    try:
        # Fetch comments from the database based on place_id
        comments = get_comments_by_place_id(db, place_id)

        # Extract comment text from each comment
        comments_list = [comment.comment_text for comment in comments]

        print("comments", comments_list)

        # Use your machine learning model to score the comments
        scores = [predict_score(comment) for comment in comments_list]

        # Calculate the average score
        avg_score = sum(scores) / len(scores)

        # Update the place rating_score in the database
        place = get_place_by_place_id(db, place_id)
        if place:
            place.rating_score = avg_score
            db.commit()
            db.refresh(place)
            return {"rating_score": avg_score}
        else:
            return create_response("error", "Place not found !", data=None)
            # raise HTTPException(status_code=404, detail="Place not found")

    except Exception as e:
        return create_response("error", f"Internal Server Error: {str(e)}", data=None)
        # raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

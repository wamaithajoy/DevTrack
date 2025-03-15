from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.database import get_db_connection
from app.auth import hash_password, verify_password, create_access_token
import mysql.connector

router = APIRouter()

# User registration request model
class UserCreate(BaseModel):
    username: str
    password: str

# User login request model
class UserLogin(BaseModel):
    username: str
    password: str

# Register new user
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    db = get_db_connection()
    cursor = db.cursor()

    # Check if username exists
    cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username already exists")

    # Insert new user
    hashed_password = hash_password(user.password)
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user.username, hashed_password))
    db.commit()
    cursor.close()
    db.close()

    return {"message": "User created successfully"}

# User login
@router.post("/login")
def login(user: UserLogin):
    db = get_db_connection()
    cursor = db.cursor()

    # Get user from DB
    cursor.execute("SELECT id, password FROM users WHERE username = %s", (user.username,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    user_id, hashed_password = result

    # Verify password
    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Generate JWT token
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

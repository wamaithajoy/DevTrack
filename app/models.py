from pydantic import BaseModel
from typing import Optional

class User:
    def __init__(self, id: int, username: str, password: str):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get_user_by_username(db, username: str):
        cursor = db.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        return User(*result) if result else None

    @staticmethod
    def create_user(db, username: str, hashed_password: str):
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        db.commit()
        cursor.close()


class TrackingData(BaseModel):
    project_name: str
    commits: Optional[int] = 0
    api_requests: Optional[int] = 0
    errors: Optional[int] = 0
    response_time: Optional[float] = 0
        

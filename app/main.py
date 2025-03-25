from fastapi import FastAPI
from app.database import get_db_connection
from app.routers import track_routes
from app.routers import users
from app.database import create_users_table 


app = FastAPI()
app.include_router(users.router)
app.include_router(track_routes.router)

@app.get("/")
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        conn.close()
        return {"message": f"Connected to database: {db_name[0]}"}
    except Exception as e:
        return {"error": str(e)}


# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_users_table()

# Include routers
app.include_router(users.router, prefix="/auth", tags=["Authentication"])

@app.get("/status")
def home():
    return {"message": "DevTrack API is running"}


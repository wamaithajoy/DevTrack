from fastapi import FastAPI
from database import get_db_connection

app = FastAPI()

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

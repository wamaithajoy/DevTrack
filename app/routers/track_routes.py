from fastapi import FastAPI
from fastapi import FastAPI, Depends, HTTPException
from app.database import get_db_connection
from app.models import TrackingData
from app.auth import get_current_user
from fastapi import APIRouter



router = APIRouter(prefix="/tracking", tags=["Tracking"])

@router.post("/")
def add_tracking_data(data: TrackingData, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO tracking (user_id, project_name, commits, api_requests, errors, response_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (current_user["id"], data.project_name, data.commits, data.api_requests, data.errors, data.response_time))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "✅ Tracking data added successfully!"}
    else:
        raise HTTPException(status_code=500, detail="❌ Database connection failed.")

# 📌 Get tracking data for a user
@router.get("/")
def get_tracking_data(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        select_query = "SELECT * FROM tracking WHERE user_id = %s"
        cursor.execute(select_query, (current_user["id"],))
        tracking_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"tracking_data": tracking_data}
    else:
        raise HTTPException(status_code=500, detail="❌ Database connection failed.")

# 📌 Update tracking data
@router.put("/")
def update_tracking_data(data: TrackingData, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        update_query = """
        UPDATE tracking 
        SET commits = %s, api_requests = %s, errors = %s, response_time = %s 
        WHERE user_id = %s AND project_name = %s
        """
        cursor.execute(update_query, (data.commits, data.api_requests, data.errors, data.response_time, current_user["id"], data.project_name))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "✅ Tracking data updated successfully!"}
    else:
        raise HTTPException(status_code=500, detail="❌ Database connection failed.")
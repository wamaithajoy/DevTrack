from fastapi import FastAPI
from fastapi import FastAPI, Depends, HTTPException, Request
from app.database import get_db_connection
from app.models import TrackingData
from app.auth import get_current_user
from fastapi import APIRouter
from datetime import datetime, timedelta
import requests



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
    
@router.delete("/{project_name}")
def delete_tracking_data(project_name: str, current_user: dict = Depends(get_current_user)):
    """
    Delete all tracking data for a project belonging to the current user.
    """
    try:
        user_id = current_user['id']
        
        db = get_db_connection()
        cursor = db.cursor()
        
        cursor.execute(
            "DELETE FROM tracking WHERE project_name = %s AND user_id = %s",
            (project_name, user_id)
        )
        
        db.commit()
        deleted = cursor.rowcount

        cursor.close()
        db.close()

        if deleted == 0:
            raise HTTPException(status_code=404, detail="Project not found or not owned by user.")
        
        return {"detail": "Project deleted successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
@router.post("/sync/{project_name}")
def sync_github_commits(project_name: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get GitHub info for this project
    cursor.execute("""
        SELECT github_repo, github_token, last_commit_date, commit_streak 
        FROM tracking 
        WHERE project_name = %s AND user_id = %s
    """, (project_name, user_id))
    project = cursor.fetchone()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    github_repo = project["github_repo"]
    github_token = project["github_token"]
    last_commit_date = project["last_commit_date"]
    prev_streak = project.get("commit_streak", 0)

    if not github_repo or not github_token:
        raise HTTPException(status_code=400, detail="GitHub repo/token missing for this project.")

    # Request commits in the past 2 days
    since = (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{github_repo}/commits?since={since}"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=f"GitHub API error: {r.status_code}")

    commits = r.json()

    if not commits:
        # No commits, check if streak should break
        if last_commit_date and (datetime.utcnow() - last_commit_date) > timedelta(days=1):
            new_streak = 0
        else:
            new_streak = prev_streak  # Maintain streak if not expired
    else:
        # New commit(s) found
        latest_commit_date = datetime.strptime(commits[0]["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")

        # Decide if the streak continues or resets
        if last_commit_date and (latest_commit_date - last_commit_date) <= timedelta(days=1):
            new_streak = prev_streak + 1
        else:
            new_streak = 1

        # Update last commit timestamp
        cursor.execute("""
            UPDATE tracking 
            SET commits = commits + %s, last_commit_date = %s, commit_streak = %s
            WHERE project_name = %s AND user_id = %s
        """, (len(commits), latest_commit_date, new_streak, project_name, user_id))
        db.commit()

    cursor.close()
    db.close()

    return {"message": f"✅ GitHub synced. Streak: {new_streak} 🔥", "commits_found": len(commits)}    
"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "チェス部": {
        "description": "チェスの戦略を学び、チェストーナメントで競う",
        "schedule": "金曜日, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "プログラミングクラス": {
        "description": "プログラミングの基礎を学び、ソフトウェアプロジェクトを構築する",
        "schedule": "火曜日と木曜日, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "体育科": {
        "description": "体育教育とスポーツ活動",
        "schedule": "月曜日、水曜日、金曜日, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "テニス部": {
        "description": "テニス技術を習得し、試合に参加する",
        "schedule": "水曜日と土曜日, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": []
    },
    "バドミントン部": {
        "description": "バドミントンの基本と戦術を学ぶ",
        "schedule": "月曜日と金曜日, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": []
    },
    "美術部": {
        "description": "絵画、彫刻、デジタルアートなどの芸術を学ぶ",
        "schedule": "木曜日, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "音楽部": {
        "description": "楽器演奏と音楽理論を学ぶ",
        "schedule": "火曜日と金曜日, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": []
    },
    "ロボット工学クラブ": {
        "description": "ロボット工学とプログラミングを学び、ロボット競技に参加する",
        "schedule": "水曜日, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "数学オリンピッククラブ": {
        "description": "数学の問題解決スキルを磨き、オリンピック大会に参加する",
        "schedule": "土曜日, 10:00 AM - 12:00 PM",
        "max_participants": 12,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Check if student is already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail=f"{email} is already signed up for {activity_name}")

    # Check if activity is full
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def cancel_signup(activity_name: str, email: str):
    """Cancel a student's signup for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Check if student is signed up
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail=f"{email} is not signed up for {activity_name}")

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Cancelled signup for {email} from {activity_name}"}

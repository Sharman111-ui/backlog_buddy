import streamlit as st
import json
import os
from datetime import datetime, timedelta
import random

DATA_FILE = "buddy_data.json"

# ---------------- Utilities ----------------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return None

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def days_left(exam_date):
    d = datetime.strptime(exam_date, "%Y-%m-%d")
    return max((d - datetime.now()).days, 1)

# ---------------- Core Logic ----------------

def generate_today_plan(data):
    backlog = data["backlog"]
    subjects = data["subjects"]
    daily_hours = data["daily_hours"]

    max_lectures = min(4, backlog)   # never overload
    tasks = []

    for i in range(max_lectures):
        sub = random.choice(subjects)
        tasks.append(f"{sub} – 1 lecture")

    return tasks

def auto_adjust(data, completed):
    if completed:
        data["backlog"] -= len(data["today_tasks"])
        data["history"].append({"date": str(datetime.now().date()), "done": True})
    else:
        data["history"].append({"date": str(datetime.now().date()), "done": False})

    data["last_day"] = str(datetime.now().date())
    return data

# ---------------- UI ----------------

st.set_page_config(page_title="Backlog Buddy", page_icon="📚")

st.title("📚 Backlog Buddy – Recovery Coach")

data = load_data()

# -------- First Time Setup --------

if data is None:

    st.subheader("Create your recovery plan")

    backlog = st.number_input("Total backlog lectures", min_value=1)
    subjects_raw = st.text_input("Subjects (comma separated)", "Physics,Chemistry,Maths")
    exam_date = st.date_input("Exam date")
    daily_hours = st.number_input("Hours you can study daily", min_value=1, max_value=12)

    if st.button("Create My Recovery Plan"):
        subjects = [s.strip() for s in subjects_raw.split(",")]

        data = {
            "backlog": backlog,
            "subjects": subjects,
            "exam_date": str(exam_date),
            "daily_hours": daily_hours,
            "history": [],
            "last_day": "",
            "today_tasks": []
        }

        save_data(data)
        st.rerun()

# -------- Main Recovery Screen --------

else:

    today = str(datetime.now().date())

    # If new day, generate fresh plan
    if data["last_day"] != today:
        data["today_tasks"] = generate_today_plan(data)
        save_data(data)

    st.markdown("### 📅 TODAY'S TASKS")

    for t in data["today_tasks"]:
        st.write("✅", t)

    st.write("---")

    if st.button("✅ Done Today"):
        data = auto_adjust(data, True)
        save_data(data)
        st.success("Nice. Plan updated for tomorrow.")
        st.rerun()

    st.write("Backlog remaining:", data["backlog"])
    st.write("Days left:", days_left(data["exam_date"]))

    # Simple weekly insight
    if len(data["history"]) >= 3:
        misses = [h for h in data["history"][-3:] if not h["done"]]
        if len(misses) >= 2:
            st.warning("You missed last days. It's okay — tomorrow will be lighter.")

    if st.button("Reset (start over)"):
        os.remove(DATA_FILE)
        st.rerun()

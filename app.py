import streamlit as st
import json
import os
from datetime import date, timedelta
import math

st.set_page_config(page_title="Backlog Buddy", page_icon="🟢")

DATA_FILE = "data.json"

# ---------------- Helpers ----------------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return None

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def reset_all():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.session_state.plan_generated = False
    st.rerun()

# ---------------- Session State ----------------

if "plan_generated" not in st.session_state:
    st.session_state.plan_generated = False

# ---------------- Load Data ----------------

data = load_data()

if not data or "subjects" not in data:
    data = {
        "subjects": [],
        "daily_load": 2,
        "start_date": date.today().isoformat()
    }
    save_data(data)

subjects = data.get("subjects", [])
daily_load = data.get("daily_load", 2)
start_date = data.get("start_date", date.today().isoformat())

# ---------------- UI ----------------

st.title("🟢 Backlog Buddy")
st.caption("Turn chaos into a daily execution plan.")

# ================= SETUP =================

if not st.session_state.plan_generated:

    st.subheader("Setup Your Backlog")

    sub_name = st.text_input("Subject Name")
    sub_backlog = st.number_input("Pending Lectures", min_value=1, step=1)

    if st.button("➕ Add Subject"):
        if sub_name.strip() != "":
            subjects.append({
                "name": sub_name.strip(),
                "backlog": sub_backlog,
                "original": sub_backlog
            })
            save_data(data)
            st.rerun()

    if len(subjects) > 0:

        st.divider()
        st.write("### Current Subjects")

        for s in subjects:
            st.write(f"- {s['name']} ({s['backlog']} lectures)")

        st.divider()

        daily_load = st.number_input(
            "Total Lectures You Can Do Per Day",
            min_value=1,
            value=daily_load,
            step=1
        )

        if st.button("Generate My Recovery Plan"):
            data["daily_load"] = daily_load
            data["start_date"] = date.today().isoformat()
            save_data(data)
            st.session_state.plan_generated = True
            st.rerun()

# ================= DASHBOARD =================

if st.session_state.plan_generated:

    st.subheader("Recovery Dashboard")

    if st.button("🔄 Reset Everything"):
        reset_all()

    total_backlog = sum(s["backlog"] for s in subjects)
    original_total = sum(s["original"] for s in subjects)

    progress = 0 if original_total == 0 else 1 - (total_backlog / original_total)

    days_needed = math.ceil(total_backlog / daily_load) if total_backlog > 0 else 0
    finish = date.fromisoformat(start_date) + timedelta(days=days_needed)

    st.progress(progress)

    st.markdown(f"""
📅 **Estimated Finish:** {finish.strftime('%d %b %Y')}  
🔥 **Progress:** {int(progress*100)}%  
📚 **Remaining Lectures:** {total_backlog}
""")

    # Motivation
    if progress < 0.3:
        st.info("Start small. Momentum > motivation.")
    elif progress < 0.7:
        st.info("Consistency phase. Don’t break the chain.")
    elif progress < 1:
        st.success("Final stretch. Finish strong.")
    else:
        st.balloons()
        st.success("🎉 Backlog Cleared. Respect.")

    st.divider()
    st.write("### Today’s Plan")

    remaining = daily_load
    today_plan = []

    temp_remaining = remaining
    for s in subjects:
        if temp_remaining <= 0:
            break
        take = min(s["backlog"], temp_remaining)
        if take > 0:
            today_plan.append((s["name"], take))
            temp_remaining -= take

    if total_backlog == 0:
        st.write("No lectures left. You’re done.")
    else:
        for name, count in today_plan:
            st.write(f"➡️ {name}: {count} lecture(s)")

    col1, col2 = st.columns(2)

    # ---------- Complete Today ----------

    with col1:
        if st.button("✅ I Completed Today"):

            remaining = daily_load

            # Fair round-robin distribution
            while remaining > 0:
                progress_made = False
                for s in subjects:
                    if s["backlog"] > 0 and remaining > 0:
                        s["backlog"] -= 1
                        remaining -= 1
                        progress_made = True
                if not progress_made:
                    break

            save_data(data)
            st.rerun()

    # ---------- Missed ----------

    with col2:
        if st.button("😔 I Missed Today"):
            st.warning("It’s okay. Come back tomorrow.")
            st.stop()

    st.divider()
    st.write("### Subject Breakdown")

    for s in subjects:
        sub_progress = 0 if s["original"] == 0 else 1 - (s["backlog"] / s["original"])
        st.write(f"{s['name']} — {s['backlog']} left")
        st.progress(sub_progress)

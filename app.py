import streamlit as st
import json
import os
from datetime import date, timedelta
import math

st.set_page_config(page_title="Backlog Buddy", page_icon="🟢")

DATA_FILE = "data.json"

# -------- Load Data --------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return None

# -------- Save Data --------
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# -------- Initialize Messages --------
if "adjustment_message" not in st.session_state:
    st.session_state.adjustment_message = ""

if "success_message" not in st.session_state:
    st.session_state.success_message = ""

# -------- Load Existing Data --------
data = load_data()

if data:
    backlog = data["backlog"]
    original_backlog = data["original_backlog"]
    daily_load = data["daily_load"]
    missed_count = data["missed_count"]
    mode = data["mode"]
    start_date = data.get("start_date", date.today().isoformat())
else:
    backlog = 0
    original_backlog = 0
    daily_load = 1
    missed_count = 0
    mode = "Normal Recovery"
    start_date = date.today().isoformat()

# -------- UI --------
st.title("🟢 Backlog Buddy")
st.subheader("Fall behind. Stay calm. We adjust.")

# -------- Setup --------
if backlog == 0:

    st.write("### Setup Your Recovery Plan")

    backlog_input = st.number_input("Total pending lectures:", min_value=1, step=1)
    daily_input = st.number_input("Planned lectures per day:", min_value=1, step=1)

    if st.button("Start Recovery Mode"):
        save_data({
            "backlog": backlog_input,
            "original_backlog": backlog_input,
            "daily_load": daily_input,
            "missed_count": 0,
            "mode": "Normal Recovery",
            "start_date": date.today().isoformat()
        })
        st.session_state.adjustment_message = ""
        st.session_state.success_message = ""
        st.rerun()

# -------- Dashboard --------
else:

    st.write("### Recovery Dashboard")

    # ---- Date Calculations ----
    start = date.fromisoformat(start_date)
    days_needed = math.ceil(backlog / daily_load)
    finish = start + timedelta(days=days_needed)

    st.markdown(
        f"""
        📅 **Started On:** {start.strftime('%d %b %Y')}  
        🏁 **Estimated Finish:** {finish.strftime('%d %b %Y')}  
        ⏳ **Days Remaining:** {days_needed}
        """
    )

    # Persistent Success Message
    if st.session_state.success_message:
        st.markdown(
            f"""
            <div style="
                padding:15px;
                border-radius:10px;
                background-color:#e8f5e9;
                border:2px solid #66bb6a;
                color:#000000;
                font-size:16px;">
                <strong>Nice Work 💪</strong><br><br>
                {st.session_state.success_message}
            </div>
            """,
            unsafe_allow_html=True
        )

    # Persistent Adjustment Message
    if st.session_state.adjustment_message:
        st.markdown(
            f"""
            <div style="
                padding:15px;
                border-radius:10px;
                background-color:#e3f2fd;
                border:2px solid #42a5f5;
                color:#000000;
                font-size:16px;">
                <strong>We Adjusted Your Plan 💙</strong><br><br>
                {st.session_state.adjustment_message}
            </div>
            """,
            unsafe_allow_html=True
        )

    # Highlight backlog
    st.markdown(
        f"<h2 style='color:green;'>Remaining Backlog: {backlog}</h2>",
        unsafe_allow_html=True
    )

    progress = 1 - (backlog / original_backlog)
    st.progress(progress)

    st.info(f"Today's Target: {daily_load}")
    st.write(f"Mode: {mode}")

    col1, col2 = st.columns(2)

    # -------- Complete --------
    with col1:
        if st.button("✅ I Completed Today"):

            backlog -= daily_load
            if backlog < 0:
                backlog = 0

            missed_count = 0
            st.session_state.adjustment_message = ""
            st.session_state.success_message = (
                f"You reclaimed {daily_load} lecture(s). Momentum maintained."
            )

            save_data({
                "backlog": backlog,
                "original_backlog": original_backlog,
                "daily_load": daily_load,
                "missed_count": missed_count,
                "mode": mode,
                "start_date": start_date
            })

            st.rerun()

    # -------- Missed --------
    with col2:
        if st.button("😔 I Missed Today"):

            missed_count += 1
            old_load = daily_load
            st.session_state.success_message = ""

            if missed_count == 1:
                st.session_state.adjustment_message = (
                    "It happens. Timeline shifted by 1 day."
                )

            elif missed_count == 2:
                daily_load = max(1, int(daily_load * 0.75))
                mode = "Adjusted Recovery"
                st.session_state.adjustment_message = (
                    f"Daily load reduced {old_load} → {daily_load}. Restart gently."
                )

            elif missed_count >= 3:
                daily_load = 1
                mode = "Minimum Viable Progress"
                st.session_state.adjustment_message = (
                    "Daily load set to 1 lecture. Momentum > speed."
                )

            save_data({
                "backlog": backlog,
                "original_backlog": original_backlog,
                "daily_load": daily_load,
                "missed_count": missed_count,
                "mode": mode,
                "start_date": start_date
            })

            st.rerun()

    # -------- Completion --------
    if backlog == 0:
        st.balloons()
        st.success("🎉 Backlog Cleared.")
        st.write("You rebuilt momentum. That’s real progress.")

        if st.button("Start New Recovery Plan"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.session_state.adjustment_message = ""
            st.session_state.success_message = ""
            st.rerun()

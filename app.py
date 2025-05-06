import streamlit as st
import os
import subprocess
import shutil

from auth_utils import (
    create_users_table, add_user, authenticate_user, reset_password,
    get_all_users, delete_user_by_id, ensure_violations_table
)

# Ensure required tables exist
create_users_table()
ensure_violations_table()

# ---------------- UI Components ---------------- #

def show_login():
    st.subheader("🔐 Login")
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate_user(email, username, password)
        if user:
            st.success(f"Welcome back, {user[1]}!")
            st.session_state.user = {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "role": user[4]
            }
        else:
            st.error("Invalid credentials.")

def show_signup():
    st.subheader("📝 Sign Up")
    email = st.text_input("Email", key="signup_email")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    role = st.selectbox("Select Role", ["User", "Admin"])

    if st.button("Register"):
        success = add_user(email, username, password, role)
        if success:
            st.success("Account created! You can log in now.")
        else:
            st.error("Username already exists.")

def show_reset_password():
    st.subheader("🔁 Reset Password")
    email = st.text_input("Email", key="reset_email")
    username = st.text_input("Username", key="reset_username")
    new_password = st.text_input("New Password", type="password", key="reset_password")

    if st.button("Reset"):
        updated = reset_password(email, username, new_password)
        if updated:
            st.success("Password updated successfully.")
        else:
            st.error("Invalid credentials or user not found.")

def show_admin_dashboard():
    st.title("👨‍💼 Admin Dashboard")
    users = get_all_users()
    st.subheader("All Registered Users")

    for user in users:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"🧑 Username: {user[1]} | 📧 Email: {user[2]} | 🛡️ Role: {user[3]}")
        with col2:
            if st.button("❌", key=user[0]):
                deleted = delete_user_by_id(user[0])
                if deleted:
                    st.success(f"Deleted {user[1]}")
                    st.rerun()
                else:
                    st.error("Delete failed.")

def show_dashboard():
    st.title("🚦 Traffic Violation Detection")
    st.write(f"Welcome, **{st.session_state.user['username']}**!")

    uploaded_video = st.file_uploader("📤 Upload a Traffic Video", type=["mp4"])
    if uploaded_video:
        video_path = os.path.join("input_videos", uploaded_video.name)
        os.makedirs("input_videos", exist_ok=True)
        with open(video_path, "wb") as f:
            f.write(uploaded_video.read())

        st.video(video_path)
        st.markdown("### 🔍 Choose Detection Module")

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        if col1.button("🪖 Helmet Detection"):
            run_detection("helmet", video_path)
        if col2.button("🚦 Signal Jumping"):
            run_detection("signal_detection", video_path)
        if col3.button("🛣️ Lane Violation"):
            run_detection("lane", video_path)
        if col4.button("🧑‍🤝‍🧑 Triple Riding"):
            run_detection("triple", video_path)

def run_detection(module_name, video_path):
    st.info(f"🚀 Running {module_name.replace('_', ' ').title()} detection...")

    script_path = os.path.join("scripts", f"{module_name}.py")

    if not os.path.exists(video_path):
        st.error(f"❌ Input video not found at: {video_path}")
        return

    if not os.path.exists(script_path):
        st.error(f"❌ Detection script not found: {script_path}")
        return

    result = subprocess.run(
        ["python3", script_path, video_path],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        st.success(f"✅ {module_name.replace('_', ' ').title()} detection complete!")

        output_video_path = f"output/{module_name}_output.mp4"
        if os.path.exists(output_video_path):
            st.video(output_video_path)

        snapshot_dir = f"output/{module_name}_violations"
        if os.path.exists(snapshot_dir):
            st.markdown("#### 📸 Snapshots of Violations")
            images = [f for f in os.listdir(snapshot_dir) if f.endswith(".jpg")]
            for img in images:
                st.image(os.path.join(snapshot_dir, img), width=400)
        else:
            st.warning("⚠️ No snapshots found.")
    else:
        st.error("❌ Detection failed with the following error:")
        st.code(result.stderr or "No error message captured.")

def show_reports():
    import sqlite3
    import pandas as pd

    st.title("📊 Violation Reports")

    try:
        conn = sqlite3.connect("violations.db")
        df = pd.read_sql_query("SELECT * FROM violations", conn)
        conn.close()

        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No violations logged yet.")
    except Exception as e:
        st.error("Failed to load reports.")
        st.code(str(e))

def show_snapshots_gallery():
    st.title("🖼️ All Snapshots Gallery")

    base_dir = "snapshots"
    if os.path.exists(base_dir):
        with st.expander("🧹 Clear All Snapshots"):
            if st.button("Delete All Snapshots"):
                shutil.rmtree(base_dir)
                os.makedirs(base_dir, exist_ok=True)
                st.success("All snapshots deleted.")
                st.rerun()

        for category in sorted(os.listdir(base_dir)):
            category_path = os.path.join(base_dir, category)
            if os.path.isdir(category_path):
                st.header(category.title())
                for date in sorted(os.listdir(category_path)):
                    date_path = os.path.join(category_path, date)
                    if os.path.isdir(date_path):
                        st.subheader(f"📅 {date}")
                        images = [img for img in os.listdir(date_path) if img.endswith(".jpg")]
                        cols = st.columns(3)
                        for idx, img in enumerate(images):
                            img_path = os.path.join(date_path, img)
                            with cols[idx % 3]:
                                st.image(img_path, caption=img, use_container_width=True)
    else:
        st.info("No snapshots available.")

import os
import streamlit as st

def show_annotated_videos():
    st.title("🎞️ Annotated Output Videos")

    video_dir = "output"
    videos = [f for f in os.listdir(video_dir) if f.endswith(".mp4")]

    with st.expander("🧹 Clear All Videos"):
        if st.button("Delete All Videos"):
            for f in videos:
                os.remove(os.path.join(video_dir, f))
            st.success("All annotated videos deleted.")
            st.rerun()

    if videos:
        for vid in videos:
            vid_path = os.path.join(video_dir, vid)
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(vid)
                st.video(vid_path)  # Make sure to pass the full path
            with col2:
                if st.button("Delete", key=vid_path):
                    os.remove(vid_path)
                    st.rerun()
    else:
        st.warning("No videos found.")

def logout():
    st.session_state.user = None
    st.success("Logged out successfully.")

# ---------------- App Navigation ---------------- #

st.set_page_config(page_title="Traffic Violation System", layout="wide")
st.sidebar.title("🚦 Navigation")

if "user" not in st.session_state:
    st.session_state.user = None

menu_options = ["Login", "Sign Up", "Reset Password"]

if st.session_state.user:
    menu_options = ["Dashboard", "Reports", "Snapshots", "Annotated Videos", "Logout"]
    if st.session_state.user["role"] == "Admin":
        menu_options.insert(1, "Admin Dashboard")

choice = st.sidebar.radio("Go to", menu_options)

if choice == "Login":
    show_login()
elif choice == "Sign Up":
    show_signup()
elif choice == "Reset Password":
    show_reset_password()
elif choice == "Dashboard":
    if st.session_state.user:
        show_dashboard()
    else:
        st.warning("Please log in to access the dashboard.")
elif choice == "Admin Dashboard":
    if st.session_state.user and st.session_state.user["role"] == "Admin":
        show_admin_dashboard()
    else:
        st.warning("Admins only. Please log in with an Admin account.")
elif choice == "Reports":
    show_reports()
elif choice == "Snapshots":
    show_snapshots_gallery()
elif choice == "Annotated Videos":
    show_annotated_videos()
elif choice == "Logout":
    logout()
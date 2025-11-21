import streamlit as st
import pandas as pd
import os
from datetime import date
import matplotlib.pyplot as plt

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="STUDENT BURNOUT LEVEL PREDICTION", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# -------------------- ADMIN CREDENTIALS --------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# -------------------- SESSION STATE --------------------
for key in ["portal", "logged_in", "username", "admin_logged_in"]:
    if key not in st.session_state:
        st.session_state[key] = False if "logged_in" in key or "admin_logged_in" in key else None if key=="portal" else ""

# -------------------- HELPER FUNCTION --------------------
def stress_category(level):
    if level <= 3:
        return "Low"
    elif 4 <= level <= 7:
        return "Moderate"
    else:
        return "High"

# -------------------- PORTAL SELECTION --------------------
if st.session_state.portal is None:
    st.markdown("<h1 style='text-align:center; color:#A3CEF1;'>🎓 STUDENT BURNOUT LEVEL PREDICTION</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👩‍🎓 User Portal", use_container_width=True):
            st.session_state.portal = "user"
            st.rerun()
    with col2:
        if st.button("🔐 Admin Portal", use_container_width=True):
            st.session_state.portal = "admin"
            st.rerun()

# -------------------- USER LOGIN --------------------
if st.session_state.portal == "user" and not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center; color:#FFB7B2;'>🔐 User Login</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        u = st.text_input("Username")
    with col2:
        p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u and p:
            st.session_state.logged_in = True
            st.session_state.username = u
            st.success(f"✅ Welcome, {u}")
            st.rerun()
        else:
            st.error("❌ Please enter username and password")

# -------------------- USER PORTAL --------------------
if st.session_state.portal == "user" and st.session_state.logged_in:
    st.sidebar.success(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.portal = None
        st.rerun()

    menu = st.sidebar.radio("📋 Menu", [
        "Dashboard", "Stress Entry", "My Progress", "Visualizations", "Awareness"
    ], index=0)

    # -------------------- DASHBOARD --------------------
    if menu == "Dashboard":
        st.markdown("<h2 style='text-align:center; color:#FEC89A;'>📊 Dashboard</h2>", unsafe_allow_html=True)
        df = pd.read_csv("student_stress_level/Stress_Dataset.csv")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", len(df))
        col2.metric("Total Parameters", len(df.columns))
        col3.metric("Average Stress Level", round(df['Stress'].mean(),2) if 'Stress' in df.columns else "N/A")
        st.dataframe(df)

    # -------------------- STRESS ENTRY --------------------
    elif menu == "Stress Entry":
        st.markdown("<h2 style='text-align:center; color:#FFD6A5;'>🧑‍🎓 Daily Stress Entry</h2>", unsafe_allow_html=True)
        with st.form("stress_form"):
            stress = st.slider("Stress Level", 1, 10, 5)
            anxiety = st.slider("Anxiety Level", 1, 10, 5)
            sleep = st.slider("Sleep Quality", 1, 10, 7)
            mood = st.selectbox("Mood", ["Happy", "Normal", "Sad", "Anxious"])
            submitted = st.form_submit_button("Submit")
            if submitted:
                new_data = {
                    "Username": st.session_state.username,
                    "Date": str(date.today()),
                    "Stress": stress,
                    "Anxiety": anxiety,
                    "Sleep": sleep,
                    "Mood": mood
                }
                file_exists = os.path.isfile("user_stress_log.csv")
                pd.DataFrame([new_data]).to_csv("user_stress_log.csv", mode="a", header=not file_exists, index=False)
                st.success("✅ Data saved successfully!")

                # Show stress prediction
                cat = stress_category(stress)
                colors = {"Low":"#A3CEF1", "Moderate":"#FFD6A5", "High":"#FF6B6B"}
                st.markdown(f"<h3 style='text-align:center; color:{colors[cat]};'>Your Stress Level Today is: {cat}</h3>", unsafe_allow_html=True)

    # -------------------- MY PROGRESS --------------------
    elif menu == "My Progress":
        st.markdown("<h2 style='text-align:center; color:#B5EAD7;'>📈 My Stress Progress</h2>", unsafe_allow_html=True)
        if os.path.isfile("user_stress_log.csv"):
            df = pd.read_csv("user_stress_log.csv")
            user_data = df[df["Username"]==st.session_state.username]
            if user_data.empty:
                st.warning("No data found for your profile.")
            else:
                st.dataframe(user_data)

                # Convert Date to datetime
                user_data["Date"] = pd.to_datetime(user_data["Date"])

                # Plot all numeric columns dynamically
                numeric_cols = user_data.select_dtypes(include=['int64', 'float64']).columns
                fig, ax = plt.subplots(figsize=(8,4))
                colors = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6A4C93"]
                for i, col in enumerate(numeric_cols):
                    ax.plot(user_data["Date"], user_data[col], marker='o', color=colors[i%len(colors)], label=col)
                ax.set_xlabel("Date")
                ax.set_ylabel("Level")
                ax.set_title("Stress, Anxiety & Sleep Over Time")
                ax.legend()
                plt.xticks(rotation=45)
                st.pyplot(fig)
        else:
            st.warning("No data file found.")

    # -------------------- VISUALIZATIONS --------------------
    elif menu == "Visualizations":
        st.markdown("<h2 style='text-align:center; color:#C7CEEA;'>📊 Stress Visualizations</h2>", unsafe_allow_html=True)
        df = pd.read_csv("student_stress_level/StressLevelDataset.csv")
        if "stress_level" in df.columns:
            st.bar_chart(df["stress_level"].value_counts())
        else:
            st.warning("No 'stress_level' column found.")

    # -------------------- AWARENESS --------------------
    elif menu == "Awareness":
        st.markdown("<h2 style='text-align:center; color:#FAD2E1;'>🌱 Mental Health Awareness</h2>", unsafe_allow_html=True)
        
        # Professional content for all categories
        st.markdown("<h3 style='color:#A3CEF1;'>Low Stress:</h3>", unsafe_allow_html=True)
        st.info("""
        ✅ Maintain your current healthy habits.  
        ✅ Balance study, work, and leisure.  
        ✅ Stay socially active and engage in hobbies.  
        ✅ Keep track of your wellbeing regularly.  
        """)
        
        st.markdown("<h3 style='color:#FFD6A5;'>Moderate Stress:</h3>", unsafe_allow_html=True)
        st.warning("""
        ⚠️ Take regular breaks during study or work.  
        ✅ Practice mindfulness, meditation, or deep breathing.  
        ✅ Stay physically active and maintain a healthy diet.  
        ✅ Avoid procrastination and manage time effectively.  
        """)
        
        st.markdown("<h3 style='color:#FF6B6B;'>High Stress:</h3>", unsafe_allow_html=True)
        st.error("""
        ❌ Your stress is high! Consider immediate action:  
        ✅ Talk to a counselor, mentor, or trusted friend.  
        ✅ Prioritize sleep, nutrition, and hydration.  
        ✅ Reduce workload and avoid burnout.  
        ✅ Practice stress-relief activities: yoga, meditation, or exercise.  
        ✅ Reflect on triggers and seek professional support if needed.  
        """)

# -------------------- ADMIN PORTAL --------------------
if st.session_state.portal == "admin":
    st.sidebar.subheader("🔐 Admin Section")
    if not st.session_state.admin_logged_in:
        admin_user = st.sidebar.text_input("Admin Username")
        admin_pass = st.sidebar.text_input("Admin Password", type="password")
        if st.sidebar.button("Admin Login"):
            if admin_user == ADMIN_USERNAME and admin_pass == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.sidebar.success("✅ Admin Logged In")
                st.rerun()
            else:
                st.sidebar.error("❌ Wrong Credentials")
    else:
        st.sidebar.success("✅ Admin Logged In")
        if st.sidebar.button("Logout Admin"):
            st.session_state.admin_logged_in = False
            st.session_state.portal = None
            st.rerun()

        admin_menu = st.sidebar.radio("📋 Admin Menu", ["Upload Dataset", "View Dataset", "Visual Reports", "Download Dataset"])
        if admin_menu == "Upload Dataset":
            st.title("📂 Upload Dataset")
            uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                df.to_csv("uploaded_dataset.csv", index=False)
                st.success("✅ Uploaded successfully")
        elif admin_menu == "View Dataset":
            st.title("📊 View Dataset")
            if os.path.exists("uploaded_dataset.csv"):
                st.dataframe(pd.read_csv("uploaded_dataset.csv"))
            else:
                st.warning("No dataset found")
        elif admin_menu == "Visual Reports":
            st.title("📈 Visual Reports")
            if os.path.exists("uploaded_dataset.csv"):
                df = pd.read_csv("uploaded_dataset.csv")
                if "stress_level" in df.columns:
                    st.bar_chart(df["stress_level"])
                else:
                    st.warning("No 'stress_level' column")
        elif admin_menu == "Download Dataset":
            st.title("⬇️ Download Dataset")
            if os.path.exists("uploaded_dataset.csv"):
                with open("uploaded_dataset.csv", "rb") as f:
                    st.download_button("Download CSV", f, "dataset.csv")







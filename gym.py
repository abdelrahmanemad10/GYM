import streamlit as st
import pandas as pd
import requests
import os
import sqlite3
import google.generativeai as genai
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------ Database Setup ------
def init_db():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'fitness_app.db')  # Database will be saved in the same directory as the script
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS weight_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            day TEXT NOT NULL,
            exercise TEXT NOT NULL,
            weight REAL NOT NULL,
            progress REAL DEFAULT 0
        )
    ''')
    conn.commit()
    return conn

# ------ Backup Database ------
def backup_db():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(script_dir, "backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup_file = os.path.join(backup_dir, f"fitness_app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    db_path = os.path.join(script_dir, 'fitness_app.db')
    with open(db_path, 'rb') as f:
        with open(backup_file, 'wb') as b:
            b.write(f.read())
    logger.info(f"Database backed up to {backup_file}")

# ------ User Registration ------
def register_user(conn, username, password):
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists

# ------ User Login ------
def login_user(conn, username, password):
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    return c.fetchone() is not None

# ------ Save Weights to DB ------
def save_weights_to_db(conn, username, date, day, exercises, weights):
    c = conn.cursor()
    for exercise, weight in zip(exercises, weights):
        c.execute('''
            SELECT weight FROM weight_tracking
            WHERE username = ? AND exercise = ?
            ORDER BY date DESC
            LIMIT 1
        ''', (username, exercise))
        last_weight = c.fetchone()
        progress = 0 if last_weight is None else weight - last_weight[0]
        c.execute('''
            INSERT INTO weight_tracking (username, date, day, exercise, weight, progress)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, date, day, exercise, weight, progress))
    conn.commit()
    logger.info(f"Weights saved for user {username} on {date}")

# ------ Get Weight History ------
def get_weight_history(conn, username):
    c = conn.cursor()
    c.execute('''
        SELECT date, day, exercise, weight, progress FROM weight_tracking
        WHERE username = ?
        ORDER BY date DESC
    ''', (username,))
    return c.fetchall()

# ------ Main Interface ------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'diet_plan' not in st.session_state:
    st.session_state.diet_plan = None

# Initialize database
conn = init_db()

# Backup database every day
if datetime.now().hour == 0 and datetime.now().minute == 0:
    backup_db()

# ------ Login/Registration System ------
if not st.session_state.logged_in:
    st.sidebar.title("🔐 تسجيل الدخول / التسجيل")
    menu = st.sidebar.radio("اختر الإجراء", ["تسجيل الدخول", "التسجيل"])

    if menu == "تسجيل الدخول":
        username = st.sidebar.text_input("اسم المستخدم")
        password = st.sidebar.text_input("كلمة المرور", type="password")
        
        if st.sidebar.button("تسجيل الدخول"):
            if login_user(conn, username, password):
                st.session_state.logged_in = True
                st.session_state.user_name = username
                st.sidebar.success("تم التسجيل بنجاح!")
            else:
                st.sidebar.error("اسم المستخدم أو كلمة المرور غير صحيحة")

    elif menu == "التسجيل":
        new_username = st.sidebar.text_input("اسم المستخدم الجديد")
        new_password = st.sidebar.text_input("كلمة المرور الجديدة", type="password")
        
        if st.sidebar.button("إنشاء حساب"):
            if register_user(conn, new_username, new_password):
                st.sidebar.success("تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
            else:
                st.sidebar.error("اسم المستخدم موجود بالفعل")

# ------ Main Interface ------
if st.session_state.logged_in:
    # ------ Sidebar ------
    with st.sidebar:
        st.title(f"مرحبًا {st.session_state.user_name}!")
        
        # Diet Plan Section
        with st.expander("🍏 خطة التغذية الشخصية"):
            age = st.number_input("العمر", 18, 80, 25)
            weight = st.number_input("الوزن (كجم)", 30.0, 150.0, 70.0)
            height = st.number_input("الطول (سم)", 140, 220, 170)
            goal = st.selectbox("الهدف", ["خسارة الوزن", "بناء العضلات", "الحفاظ على الوزن"])
            preferences = st.multiselect("التفضيلات", ["نباتي", "قليل السكر", "عالي البروتين", "خالي من الجلوتين"])
            
            if st.button("🎯 توليد الخطة"):
                diet = generate_diet(age, weight, height, goal, ", ".join(preferences))
                st.session_state.diet_plan = diet
                
        if st.session_state.diet_plan:
            st.divider()
            st.subheader("📋 خطتك الغذائية")
            st.markdown(st.session_state.diet_plan)
            
            # Download PDF Button
            if st.button("📥 تحميل الخطة كملف PDF"):
                pdf_buffer = generate_pdf(st.session_state.diet_plan)
                st.download_button(
                    label="📄 اضغط هنا لتحميل الحمية الغذائية",
                    data=pdf_buffer,
                    file_name="حمية_غذائية.pdf",
                    mime="application/pdf"
                )
            
        if st.button("تسجيل الخروج"):
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.experimental_rerun()

    # ------ Main Content ------
    st.title("🔥 برنامج اللياقة المتكامل")
    render_lottie_animation(load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_5ngs2ksb.json"))
    
    selected_day = st.selectbox("اختر يوم التمرين", workout_data["اليوم"])
    day_index = workout_data["اليوم"].index(selected_day)
    
    st.header(f"اليوم: {selected_day}")
    for i, (exercise, video) in enumerate(zip(workout_data["التمارين"][day_index], workout_data["روابط الفيديو"][day_index]), 1):
        st.subheader(f"{i}. {exercise}")
        st.video(video)
        
    # ------ Weight Tracking System ------
    st.header("🏋️ تسجيل الأوزان")
    weights = []
    for exercise in workout_data["التمارين"][day_index]:
        weight = st.number_input(f"الوزن لـ {exercise} (كجم)", 0.0, 300.0, 0.0, key=f"weight_{exercise}")
        weights.append(weight)
    
    if st.button("حفظ التقدم"):
        current_date = pd.Timestamp.now().strftime("%Y-%m-%d")
        save_weights_to_db(conn, st.session_state.user_name, current_date, selected_day, workout_data["التمارين"][day_index], weights)
        st.success("تم الحفظ بنجاح!")

    # Display Weight History
    st.header("📊 تاريخ الأوزان")
    weight_history = get_weight_history(conn, st.session_state.user_name)
    if weight_history:
        history_df = pd.DataFrame(weight_history, columns=["التاريخ", "اليوم", "التمرين", "الوزن", "التقدم"])
        st.dataframe(history_df)
    else:
        st.info("لا توجد سجلات للأوزان حتى الآن.")

else:
    st.title("اللياقة الذكية")
    st.markdown("""
    ## 🔐 يرجى تسجيل الدخول
    قم بتسجيل الدخول من الشريط الجانبي للوصول إلى:
    - برنامج التمارين المتكامل
    - خطط التغذية الذكية
    - تتبع التقدم الرياضي
    - إحصائيات شخصية
    """)
    render_lottie_animation(load_lottieurl( "https://assets9.lottiefiles.com/packages/lf20_1pxqjqps.json"))

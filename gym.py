import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
from streamlit_lottie import st_lottie  # For Lottie animations

# ------ Configure Logging ------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------ Configure Gemini API ------
genai.configure(api_key="AIzaSyCtIffUrtXoRAQKRUM8dohxop3YM34dfQc")  # Replace with your Gemini API key
model = genai.GenerativeModel('gemini-1.5-flash')

# ------ Lottie Animation Functions ------
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def render_lottie_animation(lottie_json, height=200):
    if lottie_json:
        st_lottie(lottie_json, height=height)
    else:
        st.error("Failed to load animation")

# ------ Workout Data ------
workout_data = {
    "اليوم": [
        "اليوم الأول - الدفع (Push 1) - الصدر والأكتاف والترايسبس",
        "اليوم الثاني - السحب (Pull 1) - الظهر والبايسبس والسواعد",
        "اليوم الثالث - الأرجل (Legs 1) - الرجلين والسمانة",
        "اليوم الرابع - الدفع (Push 2) - الصدر والأكتاف والترايسبس",
        "اليوم الخامس - السحب (Pull 2) - الظهر والبايسبس والسواعد",
        "اليوم السادس - الأرجل (Legs 2) - الرجلين والسمانة"
    ],
    "التمارين": [
        # Push 1 - الصدر والأكتاف والترايسبس
        [
            "تمرين الضغط بالبار",
            "تمرين الدامبلز على المقعد المائل",
            "رفرفة جانبية بالدامبلز",
            "ضغط الكتف بالبار",
            "تمرين الترايسبس بالحبل"
        ],
        # Pull 1 - الظهر والبايسبس والسواعد
        [
            "تمرين السحب الأمامي",
            "تمرين العقلة",
            "الشد العمودي بالبار",
            "تمرين البايسبس بالدامبلز",
            "تمرين تقوية الساعد بالمطرقة"
        ],
        # Legs 1 - الأرجل
        [
            "تمرين القرفصاء بالبار",
            "تمرين الرفعة الميتة الرومانية",
            "تمرين الطعن بالدامبلز",
            "تمرين سمانة واقف بالبار",
            "تمرين الساق الخلفية بالآلة"
        ],
        # Push 2 - الصدر والأكتاف والترايسبس (تنويع التمارين)
        [
            "تمرين الضغط بالدامبلز على المقعد المستوي",
            "تمرين الضغط المائل بالبار",
            "تمرين الأكتاف بالكابل من الأمام",
            "تمرين الضغط الفرنسي للترايسبس",
            "تمرين الترايسبس بالدمبل خلف الرأس"
        ],
        # Pull 2 - الظهر والبايسبس والسواعد (تنويع التمارين)
        [
            "تمرين السحب الأرضي بالبار",
            "تمرين التجديف بالدامبل بيد واحدة",
            "تمرين سحب الوجه بالكابل",
            "تمرين تركيز البايسبس",
            "تمرين لف المعصم (Wrist Curl)"
        ],
        # Legs 2 - الأرجل (تنويع التمارين)
        [
            "تمرين الرفعة الميتة التقليدية",
            "تمرين الطعن المتقدم بالدامبلز",
            "تمرين الدفع بالماكينة (Leg Press)",
            "تمرين سمانة جالس بالماكينة",
            "تمرين تمديد الساق (Leg Extension)"
        ]
    ],
    "روابط الفيديو": [
        # Push 1
        [
            "https://www.youtube.com/watch?v=rT7DgCr-3pg",  # Bench Press
            "https://www.youtube.com/watch?v=8iPEnn-ltC8",  # Incline Dumbbell Press
            "https://youtu.be/Bmgmw3qkFe4?si=MmTMOeDYmqsdMlaC",  # Lateral Raises
            "https://www.youtube.com/watch?v=2yjwXTZQDDI",  # Overhead Shoulder Press
            "https://www.youtube.com/watch?v=vB5OHsJ3EME"   # Triceps Rope Pushdown
        ],
        # Pull 1
        [
            "https://www.youtube.com/watch?v=CAwf7n6Luuc",  # Lat Pulldown
            "https://www.youtube.com/watch?v=eGo4IYlbE5g",  # Pull-ups
            "https://www.youtube.com/watch?v=GZbfZ033f74",  # Barbell Row
            "https://www.youtube.com/watch?v=ykJmrZ5v0Oo",  # Dumbbell Bicep Curls
            "https://www.youtube.com/watch?v=zC3nLlEvin4"   # Hammer Curls
        ],
        # Legs 1
        [
            "https://www.youtube.com/watch?v=Q_CuIKf227A",  # Barbell Squat
            "https://www.youtube.com/watch?v=U3HlEF_E9fo",  # Romanian Deadlift
            "https://www.youtube.com/watch?v=D7KaRcUTQeE",  # Dumbbell Lunges
            "https://www.youtube.com/watch?v=-M4-G8p8fmc",  # Standing Calf Raises
            "https://www.youtube.com/watch?v=1Tq3QdYUuHs"   # Leg Curl Machine
        ],
        # Push 2
        [
            "https://www.youtube.com/watch?v=VmB1G1K7v94",  # Flat Dumbbell Press
            "https://youtu.be/tQE1f4jsJOM?si=Pz_1BSPeuMYJewnA",  # Incline Barbell Press
            "https://www.youtube.com/watch?v=F3QY5vMz_6I",  # Front Cable Raise
            "https://www.youtube.com/watch?v=3ml7BH7mNwQ",  # French Press (Triceps)
            "https://www.youtube.com/watch?v=nRiJVZDpdL0"   # Overhead Dumbbell Triceps Extension
        ],
        # Pull 2
        [
            "https://www.youtube.com/watch?v=pYcpY20QaE8",  # Seated Cable Row
            "https://www.youtube.com/watch?v=roCP6wCXPqo",  # One-Arm Dumbbell Row
            "https://www.youtube.com/watch?v=HSoHeSjvIdY",  # Face Pulls
            "https://www.youtube.com/watch?v=kwG2ipFRgfo",  # Concentration Curl
            "https://youtu.be/J3uyPuc9304?si=7sPx2Y6eiedSWf98"   # Wrist Curl
        ],
        # Legs 2
        [
            "https://www.youtube.com/watch?v=ytGaGIn3SjE",  # Conventional Deadlift
            "https://www.youtube.com/watch?v=D7KaRcUTQeE",  # Dumbbell Step Lunges
            "https://www.youtube.com/watch?v=IZxyjW7MPJQ",  # Leg Press Machine
            "https://www.youtube.com/watch?v=1boutFjfjpU",  # Seated Calf Raises
            "https://www.youtube.com/watch?v=YyvSfVjQeL0"   # Leg Extension Machine
        ]
    ]
}

# ------ Database Setup ------
def init_db():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'fitness_app.db')
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

# ------ Diet Generation Function with Gemini ------
def generate_diet(age, weight, height, goal, preferences, budget):
    prompt = f""" انت اخصائي تغذيه خبير 
    أنا أبلغ من العمر {age} عامًا، ووزني {weight} كجم، وطولي {height} سم. هدفي هو {goal}.
    تفضيلاتي الغذائية هي: {', '.join(preferences)}.
    ميزانيتي الشهرية للطعام هي: {budget} جنيه مصري.
     الرجاء إنشاء خطة غذائية يومية مناسبة لي مع مراعاة الميزانية و مراعاة اننا في مصر واجعل اجابتك باللهجه المصريه.
    """
    response = model.generate_content(prompt)
    return response.text

# ------ PDF Generation Function ------
def generate_pdf(content):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Register Arabic font
    pdfmetrics.registerFont(TTFont('Arabic', 'arial.ttf'))
    
    # Reshape and convert Arabic text
    reshaped_text = reshape(content)
    bidi_text = get_display(reshaped_text)
    
    # Draw text on PDF
    c.setFont("Arabic", 12)
    text = c.beginText(40, 800)
    text.textLines(bidi_text)
    c.drawText(text)
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

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
            budget = st.number_input("الميزانية الشهرية للطعام (جنيه مصري)", 500, 10000, 2000)
            
            if st.button("🎯 توليد الخطة"):
                diet = generate_diet(age, weight, height, goal, preferences, budget)
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
    render_lottie_animation(load_lottieurl("https://lottie.host/fa7dc8bc-fb01-4816-ab5c-090e03203eb1/Su4GPIiaHf.json"))
    
    selected_day = st.selectbox("اختر يوم التمرين", workout_data["اليوم"])
    day_index = workout_data["اليوم"].index(selected_day)
    
    st.header(f"اليوم: {selected_day}")
    for i, (exercise, video) in enumerate(zip(workout_data["التمارين"][day_index], workout_data["روابط الفيديو"][day_index]), 1):
        st.subheader(f"{i}. {exercise}")
        st.video(video)
        
    # ------ Workout Logging and Visualization ------
    st.header("🏋️ تسجيل الأوزان")
    
    # Initialize session state for tracking workouts
    if "workouts" not in st.session_state:
        st.session_state.workouts = []

    # Workout Logging Section
    st.header("Log Your Workout")
    exercise = st.text_input("Exercise Name")
    weight = st.number_input("Weight Lifted (kg)", min_value=0.0, step=0.5)
    reps = st.number_input("Reps", min_value=1, step=1)
    add_workout = st.button("Add Workout")

    if add_workout and exercise:
        st.session_state.workouts.append({"Exercise": exercise, "Weight": weight, "Reps": reps})
        st.success("Workout added!")

    # Display Workout History
    if st.session_state.workouts:
        st.header("Workout History")
        df = pd.DataFrame(st.session_state.workouts)
        st.dataframe(df)
        
        # Visualization
        st.subheader("Progress Over Time")
        fig, ax = plt.subplots()
        df.groupby("Exercise")["Weight"].mean().plot(kind="bar", ax=ax)
        st.pyplot(fig)

    # Motivation & Engagement
    st.header("Stay Motivated!")
    st.write("Track your progress and crush your fitness goals!")

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
    render_lottie_animation(load_lottieurl("https://lottie.host/8379da38-945a-4084-8313-40ee97d290b8/KVsKyojD1Z.json"))

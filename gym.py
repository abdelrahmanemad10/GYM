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

# ------ Database Setup ------
def init_db():
    conn = sqlite3.connect('fitness_app.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

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

# ------ Lottie Animation ------
def load_lottieurl(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"خطأ في تحميل الرسوم المتحركة: {str(e)}")
        return None

def render_lottie_animation(lottie_json):
    if lottie_json:
        lottie_html = f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.7.6/lottie.min.js"></script>
        <div id="lottie"></div>
        <script>
            var animationData = {lottie_json};
            var params = {{
                container: document.getElementById('lottie'),
                renderer: 'svg',
                loop: true,
                autoplay: true,
                animationData: animationData
            }};
            lottie.loadAnimation(params);
        </script>
        """
        st.components.v1.html(lottie_html, height=200)

# ------ Diet Plan Generation ------
def generate_diet(age, weight, height, goal, preferences):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    أنا أخصائي تغذية محترف، قم بإنشاء خطة غذائية يومية مناسبة للمصريين بميزانية متوسطة (80-100 جنيه يوميًا).
    الخطة تحتوي على 5 وجبات: إفطار، سناك 1، غداء، سناك 2، عشاء.
    الوجبات تشمل أطعمة متوفرة ورخيصة مثل الفول، البيض، التونة، الفراخ، الجبنة القريش. الرجاء إنشاء خطة غذائية يومية بناء على:
    - العمر: {age}
    - الوزن: {weight} كجم
    - الطول: {height} سم
    - الهدف: {goal}
    - التفضيلات: {preferences}
    
    المتطلبات:
    - اكتب باللغة العربية المصريه العاميه
    - استخدم جدولاً منظمًا
    - أدرج 5 وجبات يومية
    - اذكر السعرات الحرارية لكل وجبة
    - قدم نصائح صحية عامة
    - تجنب المصطلحات المعقدة
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"خطأ في توليد الخطة: {str(e)}"

# ------ PDF Generation ------
def generate_pdf(diet_text):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("الخطة الغذائية")

    # Register a font that supports Arabic
    font_path = "fonts/Arial Unicode MS.ttf.TTF"  # Update this path if necessary
    pdfmetrics.registerFont(TTFont('ArialUnicode', font_path))

    # إعداد النصوص للطباعة بالعربية
    reshaped_text = reshape(diet_text)
    bidi_text = get_display(reshaped_text)

    # رسم النص على ملف الـ PDF
    pdf.setFont("ArialUnicode", 6)
    pdf.drawString(100, 800, "📋 خطتك الغذائية اليومية:")
    
    y = 780
    for line in bidi_text.split("\n"):
        pdf.drawString(100, y, line)
        y -= 20

    pdf.save()
    buffer.seek(0)
    return buffer

# ------ Workout Data ------
workout_data = {
    "اليوم": ["Push 1", "Pull 1", "Legs 1", "Push 2", "Pull 2", "Legs 2"],
    "التمارين": [
        ["Bench Press", "Incline Dumbbell Press", "Overhead Shoulder Press", "Lateral Raises", "Dips", "Cable Triceps Pushdown"],
        ["Deadlift", "Pull-Ups", "Barbell Row", "Face Pulls", "Barbell Biceps Curl", "Hammer Curl"],
        ["Squat", "Romanian Deadlift", "Leg Press", "Leg Curl", "Standing Calf Raises"],
        ["Incline Barbell Press", "Dumbbell Shoulder Press", "Cable Flys", "Lateral Raises (Drop Set)", "Skull Crushers", "Rope Triceps Extensions"],
        ["Rack Pulls", "Lat Pulldown", "Seated Cable Row", "Reverse Flys", "Concentration Curl", "Preacher Curl"],
        ["Front Squat", "Bulgarian Split Squat", "Lying Hamstring Curl", "Seated Calf Raises", "Ab Wheel Rollouts"]
    ],
    "روابط الفيديو": [
        ["https://www.youtube.com/watch?v=rT7DgCr-3pg", "https://www.youtube.com/watch?v=8iPEnn-ltC8", "https://www.youtube.com/watch?v=HzIiNhHhhtA", "https://www.youtube.com/watch?v=3VcKaXpzqRo", "https://www.youtube.com/watch?v=2z8JmcrW-As", "https://www.youtube.com/watch?v=vB5OHsJ3EME"],
        ["https://www.youtube.com/watch?v=1ZXobu7JvvE", "https://www.youtube.com/watch?v=LHDNcCw7kF8", "https://www.youtube.com/watch?v=GZbfZ033f74", "https://www.youtube.com/watch?v=VT-O6YIP-II", "https://www.youtube.com/watch?v=kwG2ipFRgfo", "https://www.youtube.com/watch?v=TwD-YGVP4Bk"],
        ["https://www.youtube.com/watch?v=YaXPRqUwItQ", "https://www.youtube.com/watch?v=2SHsk9AzdjA", "https://www.youtube.com/watch?v=IZxyjW7MPJQ", "https://www.youtube.com/watch?v=1Tq3QdYUuHs", "https://www.youtube.com/shorts/IrrmU7_swBI"],
        ["https://www.youtube.com/watch?v=lJ2o89kcnxY", "https://www.youtube.com/watch?v=B-aVuyhvLHU", "https://www.youtube.com/watch?v=taI4XduLpTk", "https://www.youtube.com/watch?v=3VcKaXpzqRo", "https://www.youtube.com/watch?v=d_KZxkY_0cM", "https://www.youtube.com/watch?v=2-LAMcpzODU"],
        ["https://www.youtube.com/watch?v=tSvkOEKT7sg", "https://www.youtube.com/watch?v=CAwf7n6Luuc", "https://www.youtube.com/watch?v=GZbfZ033f74", "https://www.youtube.com/watch?v=5YK4bgzXDp0", "https://www.youtube.com/watch?v=soxrZlIl35U", "https://www.youtube.com/watch?v=sxA__DoLsgo"],
        ["https://www.youtube.com/watch?v=1oed-UmAxFs", "https://www.youtube.com/watch?v=2C-uNgKwPLE", "https://www.youtube.com/watch?v=1Tq3QdYUuHs", "https://www.youtube.com/watch?v=YyvSfVjQeL0", "https://www.youtube.com/watch?v=6GMKPQVERzw"]
    ]
}

# ------ Session State Management ------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'diet_plan' not in st.session_state:
    st.session_state.diet_plan = None

# ------ Database Connection ------
conn = init_db()

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
        history_df = pd.DataFrame({
            "التاريخ": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "اليوم": selected_day,
            "التمارين": workout_data["التمارين"][day_index],
            "الأوزان": weights
        })
        history_df.to_csv("fitness_history.csv", mode="a", header=not os.path.exists("fitness_history.csv"), index=False)
        st.success("تم الحفظ بنجاح!")

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
    render_lottie_animation(load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_5itoumpj.json"))

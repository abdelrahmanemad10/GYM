import streamlit as st
import sqlite3
import pandas as pd

# إنشاء قاعدة البيانات
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

# إنشاء جدول المستخدمين إذا لم يكن موجودًا
c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                password TEXT,
                weight REAL,
                height REAL
            )''')

# إنشاء جدول لتخزين تقدم المستخدم في الأوزان
c.execute('''CREATE TABLE IF NOT EXISTS progress (
                user_id INTEGER,
                exercise TEXT,
                weight_used REAL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''')
conn.commit()

def register_user(name, email, password, weight, height):
    """إضافة مستخدم جديد إلى قاعدة البيانات"""
    try:
        c.execute("INSERT INTO users (name, email, password, weight, height) VALUES (?, ?, ?, ?, ?)", 
                  (name, email, password, weight, height))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(email, password):
    """التحقق من تسجيل دخول المستخدم"""
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    return c.fetchone()

def save_progress(user_id, exercise, weight_used):
    """حفظ تقدم المستخدم في الأوزان"""
    c.execute("INSERT INTO progress (user_id, exercise, weight_used) VALUES (?, ?, ?)", 
              (user_id, exercise, weight_used))
    conn.commit()

# جدول التمارين مع روابط الفيديو
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
        ["https://www.youtube.com/watch?v=1ZXobu7JvvE", "https://www.youtube.com/watch?v=eGo4IYlbE5g", "https://www.youtube.com/watch?v=GZbfZ033f74", "https://www.youtube.com/watch?v=-M4-G8p8fmc", "https://www.youtube.com/watch?v=kwG2ipFRgfo", "https://www.youtube.com/watch?v=TwD-YGVP4Bk"],
        ["https://www.youtube.com/watch?v=YaXPRqUwItQ", "https://www.youtube.com/watch?v=2SHsk9AzdjA", "https://www.youtube.com/watch?v=IZxyjW7MPJQ", "https://www.youtube.com/watch?v=1Tq3QdYUuHs", "https://www.youtube.com/watch?v=SG1-FJqIjRU"],
        ["https://www.youtube.com/watch?v=lJ2o89kcnxY", "https://www.youtube.com/watch?v=B-aVuyhvLHU", "https://www.youtube.com/watch?v=taI4XduLpTk", "https://www.youtube.com/watch?v=3VcKaXpzqRo", "https://www.youtube.com/watch?v=d_KZxkY_0cM", "https://www.youtube.com/watch?v=2-LAMcpzODU"],
        ["https://www.youtube.com/watch?v=tSvkOEKT7sg", "https://www.youtube.com/watch?v=CAwf7n6Luuc", "https://www.youtube.com/watch?v=GZbfZ033f74", "https://www.youtube.com/watch?v=5YK4bgzXDp0", "https://www.youtube.com/watch?v=soxrZlIl35U", "https://www.youtube.com/watch?v=sxA__DoLsgo"],
        ["https://www.youtube.com/watch?v=1oed-UmAxFs", "https://www.youtube.com/watch?v=2C-uNgKwPLE", "https://www.youtube.com/watch?v=1Tq3QdYUuHs", "https://www.youtube.com/watch?v=YyvSfVjQeL0", "https://www.youtube.com/watch?v=6GMKPQVERzw"]
    ]
}

# واجهة التطبيق
st.title("🔥 تسجيل الدخول والتسجيل")

menu = ["تسجيل الدخول", "إنشاء حساب", "جدول التمارين"]
choice = st.sidebar.selectbox("اختر الصفحة", menu)

if choice == "إنشاء حساب":
    st.subheader("🔹 إنشاء حساب جديد")
    name = st.text_input("الاسم الكامل")
    email = st.text_input("البريد الإلكتروني")
    password = st.text_input("كلمة المرور", type="password")
    weight = st.number_input("وزنك الحالي (كجم)", min_value=30.0, max_value=200.0, value=70.0)
    height = st.number_input("طولك (سم)", min_value=100.0, max_value=250.0, value=170.0)
    if st.button("🔐 تسجيل"): 
        if register_user(name, email, password, weight, height):
            st.success("🎉 تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.")
        else:
            st.error("⚠️ البريد الإلكتروني مسجل بالفعل.")

elif choice == "تسجيل الدخول":
    st.subheader("🔹 تسجيل الدخول")
    email = st.text_input("البريد الإلكتروني")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("🚀 دخول"):
        user = login_user(email, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user[0]
            st.session_state["user_name"] = user[1]
            st.success(f"🎉 مرحبًا، {user[1]}!")
        else:
            st.error("❌ البريد الإلكتروني أو كلمة المرور غير صحيحة.")

if "logged_in" in st.session_state and st.session_state["logged_in"] and choice == "جدول التمارين":
    st.title("🔥 جدول تمرين Push Pull Legs")
    st.write("💪 جدول تمرين لمدة 6 أيام مناسب لزيادة الكتلة العضلية وتقليل الدهون.")
    selected_day = st.sidebar.selectbox("اختر اليوم", workout_data["اليوم"])
    index = workout_data["اليوم"].index(selected_day)
    st.header(f"📌 اليوم: {selected_day}")
    for j, exercise in enumerate(workout_data["التمارين"][index]):
        st.write(f"{j+1}. {exercise}")
        st.video(workout_data["روابط الفيديو"][index][j])
        exercise_weight = st.number_input(f"أدخل الوزن المستخدم في {exercise} (كجم)", 
                                          min_value=0.0, max_value=500.0, value=0.0, key=f"weight_{index}_{j}")
        if st.button(f"💾 حفظ التقدم في {exercise}", key=f"save_{index}_{j}"):
            save_progress(st.session_state["user_id"], exercise, exercise_weight)
            st.success(f"✅ تم حفظ تقدمك في {exercise}!")
    st.write("✅ تأكد من زيادة الأحمال تدريجيًا والتغذية السليمة.")

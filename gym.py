import streamlit as st
import pandas as pd

# جدول التمارين
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
        ["https://www.youtube.com/watch?v=YaXPRqUwItQ", "https://www.youtube.com/watch?v=2SHsk9AzdjA", "https://www.youtube.com/watch?v=IZxyjW7MPJQ", "https://www.youtube.com/watch?v=1Tq3QdYUuHs", "https://www.youtube.com/shorts/IrrmU7_swBI"],
        ["https://www.youtube.com/watch?v=lJ2o89kcnxY", "https://www.youtube.com/watch?v=B-aVuyhvLHU", "https://www.youtube.com/watch?v=taI4XduLpTk", "https://www.youtube.com/watch?v=3VcKaXpzqRo", "https://www.youtube.com/watch?v=d_KZxkY_0cM", "https://www.youtube.com/watch?v=2-LAMcpzODU"],
        ["https://www.youtube.com/watch?v=tSvkOEKT7sg", "https://www.youtube.com/watch?v=CAwf7n6Luuc", "https://www.youtube.com/watch?v=GZbfZ033f74", "https://www.youtube.com/watch?v=5YK4bgzXDp0", "https://www.youtube.com/watch?v=soxrZlIl35U", "https://www.youtube.com/watch?v=sxA__DoLsgo"],
        ["https://www.youtube.com/watch?v=1oed-UmAxFs", "https://www.youtube.com/watch?v=2C-uNgKwPLE", "https://www.youtube.com/watch?v=1Tq3QdYUuHs", "https://www.youtube.com/watch?v=YyvSfVjQeL0", "https://www.youtube.com/watch?v=6GMKPQVERzw"]
    ]
}

# Sidebar for user input
st.sidebar.title("🔍 تصفية حسب اليوم")
selected_day = st.sidebar.selectbox("اختر اليوم", workout_data["اليوم"])

st.sidebar.title("⚖️ تسجيل الوزن")
weight = st.sidebar.number_input("أدخل وزنك (كجم)", min_value=30.0, max_value=200.0, value=64.0)
st.sidebar.write(f"✅ وزنك الحالي: {weight} كجم")

st.sidebar.title("👤 معلومات المستخدم")
user_name = st.sidebar.text_input("أدخل اسمك")

# Main content
st.title("🔥 جدول تمرين Push Pull Legs")
st.write("💪 جدول تمرين لمدة 6 أيام مناسب لزيادة الكتلة العضلية وتقليل الدهون.")

if user_name:
    st.write(f"مرحبًا، {user_name}!")

index = workout_data["اليوم"].index(selected_day)
st.header(f"📌 اليوم: {selected_day}")
for j, exercise in enumerate(workout_data["التمارين"][index]):
    st.write(f"{j+1}. {exercise}")
    st.video(workout_data["روابط الفيديو"][index][j])
    exercise_weight = st.number_input(f"أدخل الوزن المستخدم في {exercise} (كجم)", min_value=0.0, max_value=500.0, value=0.0, key=f"weight_{index}_{j}")

st.write("✅ تأكد من زيادة الأحمال تدريجيًا والتغذية السليمة.")

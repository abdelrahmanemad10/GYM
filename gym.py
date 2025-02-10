import streamlit as st
import pandas as pd
import requests
import os

# Function to load Lottie animations with error handling
def load_lottieurl(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "application/json",
        }
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()  # Raise exception for bad status codes
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading animation: {str(e)}")
        return None

# Function to render Lottie animation using HTML
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
    else:
        st.warning("Animation could not be loaded")

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
        ["https://www.youtube.com/watch?v=1ZXobu7JvvE", "https://www.youtube.com/watch?v=LHDNcCw7kF8", "https://www.youtube.com/watch?v=GZbfZ033f74", "https://www.youtube.com/watch?v=VT-O6YIP-II", "https://www.youtube.com/watch?v=kwG2ipFRgfo", "https://www.youtube.com/watch?v=TwD-YGVP4Bk"],
        ["https://www.youtube.com/watch?v=YaXPRqUwItQ", "https://www.youtube.com/watch?v=2SHsk9AzdjA", "https://www.youtube.com/watch?v=IZxyjW7MPJQ", "https://www.youtube.com/watch?v=1Tq3QdYUuHs", "https://www.youtube.com/shorts/IrrmU7_swBI"],
        ["https://www.youtube.com/watch?v=lJ2o89kcnxY", "https://www.youtube.com/watch?v=B-aVuyhvLHU", "https://www.youtube.com/watch?v=taI4XduLpTk", "https://www.youtube.com/watch?v=3VcKaXpzqRo", "https://www.youtube.com/watch?v=d_KZxkY_0cM", "https://www.youtube.com/watch?v=2-LAMcpzODU"],
        ["https://www.youtube.com/watch?v=tSvkOEKT7sg", "https://www.youtube.com/watch?v=CAwf7n6Luuc", "https://www.youtube.com/watch?v=GZbfZ033f74", "https://www.youtube.com/watch?v=5YK4bgzXDp0", "https://www.youtube.com/watch?v=soxrZlIl35U", "https://www.youtube.com/watch?v=sxA__DoLsgo"],
        ["https://www.youtube.com/watch?v=1oed-UmAxFs", "https://www.youtube.com/watch?v=2C-uNgKwPLE", "https://www.youtube.com/watch?v=1Tq3QdYUuHs", "https://www.youtube.com/watch?v=YyvSfVjQeL0", "https://www.youtube.com/watch?v=6GMKPQVERzw"]
    ]
}

# File to store exercise weights history
history_file = "exercise_weights_history.csv"

# Load history if it exists
if os.path.exists(history_file):
    history_df = pd.read_csv(history_file)
else:
    history_df = pd.DataFrame(columns=["User", "Day", "Exercise", "Weight"])

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# Login form
if not st.session_state.logged_in:
    st.sidebar.title("🔐 تسجيل الدخول")
    user_name = st.sidebar.text_input("اسم المستخدم")
    user_password = st.sidebar.text_input("كلمة المرور", type="password")
    login_button = st.sidebar.button("تسجيل الدخول")

    if login_button:
        # Simple authentication (replace with proper authentication in production)
        if user_name and user_password:  # Basic validation
            st.session_state.logged_in = True
            st.session_state.user_name = user_name
            st.sidebar.success(f"تم تسجيل الدخول بنجاح! مرحبًا، {user_name}")
        else:
            st.sidebar.error("يرجى ملء جميع الحقول")
else:
    st.sidebar.success(f"مرحبًا، {st.session_state.user_name}!")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.experimental_rerun()

# Main content
if st.session_state.logged_in:
    st.title("🔥 جدول تمرين Push Pull Legs")
    st.write("💪 جدول تمرين لمدة 6 أيام مناسب لزيادة الكتلة العضلية وتقليل الدهون.")

    # Load and display Lottie animation
    lottie_animation = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_5ngs2ksb.json")
    render_lottie_animation(lottie_animation)

    selected_day = st.sidebar.selectbox("اختر اليوم", workout_data["اليوم"])

    index = workout_data["اليوم"].index(selected_day)
    st.header(f"📌 اليوم: {selected_day}")

    current_session_weights = []

    for j, exercise in enumerate(workout_data["التمارين"][index]):
        st.write(f"{j+1}. {exercise}")
        
        # Handle video URLs
        video_url = workout_data["روابط الفيديو"][index][j]
        if video_url.startswith("http"):
            st.video(video_url)
        else:
            st.warning("رابط الفيديو غير صالح")
        
        exercise_weight = st.number_input(
            f"أدخل الوزن المستخدم في {exercise} (كجم)",
            min_value=0.0,
            max_value=500.0,
            value=0.0,
            key=f"weight_{index}_{j}"
        )
        current_session_weights.append({
            "User": st.session_state.user_name,
            "Day": selected_day,
            "Exercise": exercise,
            "Weight": exercise_weight
        })

    if st.button("حفظ الأوزان"):
        new_history_df = pd.DataFrame(current_session_weights)
        history_df = pd.concat([history_df, new_history_df], ignore_index=True)
        history_df.to_csv(history_file, index=False)
        st.success("تم حفظ الأوزان بنجاح!")

    st.header("📜 تاريخ الأوزان")
    user_history_df = history_df[history_df["User"] == st.session_state.user_name]
    if not user_history_df.empty:
        st.dataframe(user_history_df)
    else:
        st.write("لا يوجد تاريخ للأوزان لهذا المستخدم.")

    st.write("✅ تأكد من زيادة الأحمال تدريجيًا والتغذية السليمة.")
else:
    st.title("🔐 يرجى تسجيل الدخول للوصول إلى جدول التمرين")

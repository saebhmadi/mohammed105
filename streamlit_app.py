import streamlit as st
import yfinance as yf
import google.generativeai as genai
from datetime import datetime, timedelta
from PIL import Image

# -------------------------
# إعداد الصفحة والتصميم
# -------------------------
st.set_page_config(page_title="التداول المظلم | محمد", layout="wide")
st.markdown("""
<style>
.main { background-color: #000000; color: #00ff00; }
.stApp { background-color: #000000; }
h1, h2, h3 { color: #ffffff !important; }
.stButton>button { background-color: #1e1e1e; color: #00ff00; border: 1px solid #00ff00; width: 100%; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# مفتاح Gemini من Secrets
# -------------------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ لم يتم ضبط GEMINI_API_KEY داخل Secrets في Streamlit Cloud.")
    st.info("افتح Manage app → Settings/Secrets وأضف المفتاح ثم أعد تشغيل التطبيق.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------
# نظام 3 أيام (تجريبي)
# -------------------------
if "join_date" not in st.session_state:
    st.session_state.join_date = datetime.now()

expire_date = st.session_state.join_date + timedelta(days=3)
is_expired = datetime.now() > expire_date

if is_expired:
    st.error("⚠️ انتهت الفترة التجريبية (3 أيام)")
    st.subheader("للتفعيل والحصول على اشتراك شهري، تواصل مع الدعم الفني:")
    st.markdown("[📞 اضغط هنا للتواصل واتساب](https://wa.me/966XXXXXXXXX)")
    st.stop()

st.title("🛡️ منصة التداول المظلم - بإدارة محمد")
remaining_days = (expire_date - datetime.now()).days + 1
st.sidebar.success(f"🔓 وصول مجاني: متبقي {remaining_days} أيام")

# -------------------------
# واجهة التطبيق
# -------------------------
col1, col2 = st.columns([1.5, 2])

with col1:
    st.subheader("💬 محادثة ودعم فني ذكي")
    user_query = st.text_input("اسأل عن سعر الذهب أو تأثير الأخبار...")
    if user_query:
        with st.spinner("جاري توليد الرد..."):
            response = model.generate_content(f"أجب كخبير تداول محترف عن: {user_query}")
        st.info(response.text)

with col2:
    st.subheader("📈 السعر الحي")
    try:
        gold_data = yf.Ticker("GC=F").history(period="1d")
        if gold_data.empty:
            st.warning("تعذر جلب بيانات الذهب الآن. حاول لاحقًا.")
        else:
            current_price = gold_data["Close"].iloc[-1]
            st.metric("سعر الذهب العالمي (GC=F)", value=f"${current_price:.2f}", delta="Live")
    except Exception as e:
        st.warning("تعذر جلب السعر الحي الآن.")
        st.caption(str(e))

    st.subheader("📸 تحليل الشارت (رادار الذيول)")
    file = st.file_uploader("ارفع صورة الشارت هنا", type=["png", "jpg", "jpeg"])
    if file:
        img = Image.open(file)
        st.image(img, caption="جاري فحص السيولة الذيول...")

        if st.button("🚀 استخراج صفقة فورية"):
            prompt = (
                "حلل صورة الشارت هذه. ابحث عن ذيول الشموع الطويلة ومناطق الدعم/المقاومة. "
                "أعطني: نقطة دخول، هدف أول، هدف ثاني، ووقف خسارة. مع سبب مختصر."
            )
            with st.spinner("جاري تحليل الصورة..."):
                res = model.generate_content([prompt, img])
            st.success("التحليل الفني للذكاء الاصطناعي:")
            st.write(res.text)

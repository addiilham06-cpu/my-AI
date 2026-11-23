
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

st.set_page_config(page_title="Study AI", page_icon="📚")

st.title("📚 Study AI")
st.caption("مساعدك الدراسي الذكي")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("تأكد من وجود مفتاح Gemini في ملف .env")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL = "gemini-3.5-flash-lite"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.divider()

st.subheader("💬 اسأل مساعدك")
question = st.chat_input("اكتب سؤالك الدراسي...")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("أفكر..."):
            try:
                response = client.models.generate_content(
                    model=MODEL,
                    contents=question
                )
                answer = response.text or "لم أجد إجابة."

            except Exception as e:
                answer = f"حدث خطأ: {e}"

            st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

st.divider()
st.subheader("📸 حل تمرين من صورة")

uploaded_image = st.file_uploader(
    "اختر صورة التمرين",
    type=["png", "jpg", "jpeg"]
)

if uploaded_image:
    st.image(uploaded_image, caption="صورة التمرين", width=400)

    if st.button("حل التمرين"):
        with st.spinner("أقرأ التمرين وأحلّه..."):
            try:
                image_part = types.Part.from_bytes(
                    data=uploaded_image.getvalue(),
                    mime_type=uploaded_image.type
                )

                response = client.models.generate_content(
                    model=MODEL,
                    contents=[
                        "اقرأ التمرين الموجود في الصورة، ثم حلّه "
                        "بالعربية مع شرح الخطوات بالتفصيل. "
                        "إذا كانت الصورة غير واضحة، أخبر الطالب.",
                        image_part
                    ]
                )

                answer = response.text or "لم أتمكن من قراءة الصورة."

                st.success("تم تحليل الصورة!")
                st.markdown(answer)

            except Exception as e:
                st.error(f"حدث خطأ: {e}")

if st.button("مسح المحادثة"):
    st.session_state.messages = []
    st.rerun()

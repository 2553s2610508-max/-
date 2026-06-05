import streamlit as st
from google import genai

# 페이지 설정
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💖"
)

st.title("💖 연애상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반")

# API 키 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("GEMINI_API_KEY가 Secrets에 설정되지 않았습니다.")
    st.stop()

# Gemini 클라이언트 생성
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gemini 초기화 오류: {e}")
    st.stop()

# 채팅 기록 유지
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요. 연애 고민을 편하게 이야기해 주세요."
        }
    ]

# 이전 대화 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력
prompt = st.chat_input("연애 고민을 입력하세요")

if prompt:
    # 사용자 메시지 저장
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # 대화 기록 생성
        history = []

        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            history.append(
                {
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                }
            )

        system_prompt = """
        당신은 공감 능력이 뛰어난 연애상담 전문가입니다.

        규칙:
        - 친절하고 따뜻하게 답변
        - 현실적인 조언 제공
        - 비난하지 않기
        - 한국어로 답변
        - 너무 긴 답변은 피하기
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": system_prompt}]
                },
                *history
            ]
        )

        answer = response.text

    except Exception as e:
        answer = f"오류가 발생했습니다.\n\n{str(e)}"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

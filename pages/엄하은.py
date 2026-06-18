import streamlit as st
import json
import os
from datetime import datetime
import uuid

st.set_page_config(
    page_title="학급 건의함",
    page_icon="📮",
    layout="wide"
)

DATA_FILE = "suggestions.json"


# -------------------------
# 데이터 저장/불러오기
# -------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# -------------------------
# 데이터 로드
# -------------------------
if "suggestions" not in st.session_state:
    st.session_state.suggestions = load_data()


# -------------------------
# 제목
# -------------------------
st.title("📮 학급 건의함")
st.caption("학급을 더 좋게 만들기 위한 의견을 자유롭게 남겨보세요!")


# -------------------------
# 메뉴
# -------------------------
menu = st.sidebar.radio(
    "메뉴 선택",
    ["✏️ 건의하기", "📋 건의 게시판"]
)

# ===================================================
# 건의하기 페이지
# ===================================================
if menu == "✏️ 건의하기":

    st.subheader("건의 작성")

    category = st.selectbox(
        "건의 종류",
        [
            "시설",
            "수업",
            "급식",
            "행사",
            "학급 규칙",
            "기타"
        ]
    )

    title = st.text_input("제목")

    content = st.text_area(
        "건의 내용",
        height=200
    )

    anonymous = st.checkbox(
        "익명으로 작성",
        value=True
    )

    if st.button("📨 건의 제출", use_container_width=True):

        if not title.strip():
            st.warning("제목을 입력해주세요.")
        elif not content.strip():
            st.warning("내용을 입력해주세요.")
        else:

            suggestion = {
                "id": str(uuid.uuid4()),
                "category": category,
                "title": title.strip(),
                "content": content.strip(),
                "writer": "익명" if anonymous else "학생",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            st.session_state.suggestions.append(suggestion)
            save_data(st.session_state.suggestions)

            st.success("건의가 등록되었습니다! 🎉")


# ===================================================
# 게시판 페이지
# ===================================================
else:

    st.subheader("건의 게시판")

    categories = [
        "전체",
        "시설",
        "수업",
        "급식",
        "행사",
        "학급 규칙",
        "기타"
    ]

    selected = st.selectbox(
        "카테고리 선택",
        categories
    )

    suggestions = st.session_state.suggestions

    if selected != "전체":
        suggestions = [
            s for s in suggestions
            if s["category"] == selected
        ]

    suggestions = list(reversed(suggestions))

    if not suggestions:
        st.info("등록된 건의가 없습니다.")
    else:

        for item in suggestions:

            with st.container():

                st.markdown(
                    f"""
### {item['title']}
**분류:** {item['category']}  
**작성자:** {item['writer']}  
**작성일:** {item['time']}
"""
                )

                st.write(item["content"])

                if st.button(
                    "🗑️ 삭제",
                    key=item["id"]
                ):

                    st.session_state.suggestions = [
                        s for s in st.session_state.suggestions
                        if s["id"] != item["id"]
                    ]

                    save_data(
                        st.session_state.suggestions
                    )

                    st.success("삭제되었습니다.")
                    st.rerun()

                st.divider()

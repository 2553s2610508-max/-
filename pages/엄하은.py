import streamlit as st
import sqlite3
from datetime import datetime

# -------------------------
# DB 설정
# -------------------------
conn = sqlite3.connect("suggestions.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    content TEXT,
    created_at TEXT
)
""")
conn.commit()

# -------------------------
# 함수
# -------------------------
def add_suggestion(category, content):
    cursor.execute(
        """
        INSERT INTO suggestions(category, content, created_at)
        VALUES (?, ?, ?)
        """,
        (category, content, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()


def get_suggestions(category=None):
    if category and category != "전체":
        cursor.execute(
            """
            SELECT * FROM suggestions
            WHERE category=?
            ORDER BY id DESC
            """,
            (category,)
        )
    else:
        cursor.execute(
            """
            SELECT * FROM suggestions
            ORDER BY id DESC
            """
        )

    return cursor.fetchall()


def delete_suggestion(suggestion_id):
    cursor.execute(
        """
        DELETE FROM suggestions
        WHERE id=?
        """,
        (suggestion_id,)
    )
    conn.commit()


# -------------------------
# 화면 설정
# -------------------------
st.set_page_config(
    page_title="학급 건의함",
    page_icon="📮",
    layout="wide"
)

st.title("📮 학급 건의함")
st.caption("익명으로 자유롭게 건의해 주세요!")

# -------------------------
# 사이드바
# -------------------------
st.sidebar.header("📊 현황")

cursor.execute("SELECT COUNT(*) FROM suggestions")
total = cursor.fetchone()[0]

st.sidebar.metric("총 건의 수", total)

# -------------------------
# 건의 작성
# -------------------------
st.subheader("✏️ 건의하기")

categories = [
    "수업",
    "행사",
    "환경",
    "규칙",
    "기타"
]

with st.form("suggestion_form", clear_on_submit=True):
    category = st.selectbox(
        "건의 종류",
        categories
    )

    content = st.text_area(
        "건의 내용",
        placeholder="건의 내용을 입력하세요."
    )

    submit = st.form_submit_button("등록하기")

    if submit:
        if not content.strip():
            st.error("건의 내용을 입력해주세요.")
        else:
            try:
                add_suggestion(category, content)
                st.success("건의가 등록되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"오류 발생: {e}")

st.divider()

# -------------------------
# 게시판
# -------------------------
st.subheader("📋 건의 게시판")

filter_category = st.selectbox(
    "카테고리 선택",
    ["전체"] + categories
)

suggestions = get_suggestions(filter_category)

if not suggestions:
    st.info("등록된 건의가 없습니다.")
else:
    for suggestion in suggestions:
        suggestion_id = suggestion[0]
        category = suggestion[1]
        content = suggestion[2]
        created_at = suggestion[3]

        with st.container(border=True):

            col1, col2 = st.columns([8, 1])

            with col1:
                st.markdown(
                    f"""
                    **[{category}]**

                    {content}

                    ⏰ {created_at}
                    """
                )

            with col2:
                if st.button(
                    "🗑️",
                    key=f"delete_{suggestion_id}"
                ):
                    try:
                        delete_suggestion(suggestion_id)
                        st.success("삭제되었습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"삭제 실패: {e}")

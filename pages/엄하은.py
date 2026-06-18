import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="학급 건의함",
    page_icon="📮",
    layout="wide"
)

# -----------------------------
# 스타일
# -----------------------------
st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.card {
    padding:15px;
    border-radius:15px;
    background-color:#f8fafc;
    border:1px solid #e5e7eb;
    margin-bottom:12px;
}

.big-title{
    text-align:center;
    font-size:40px;
    font-weight:bold;
    color:#2563eb;
}

.subtitle{
    text-align:center;
    color:gray;
    margin-bottom:20px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DB 연결
# -----------------------------
conn = sqlite3.connect(
    "suggestions.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS suggestions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    content TEXT,
    likes INTEGER DEFAULT 0,
    created_at TEXT
)
""")

conn.commit()

# -----------------------------
# 함수
# -----------------------------
def add_suggestion(category, content):
    cursor.execute("""
    INSERT INTO suggestions
    (category, content, likes, created_at)
    VALUES (?, ?, ?, ?)
    """,
    (
        category,
        content,
        0,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()


def get_suggestions(category="전체", sort="최신순"):

    order = "id DESC"

    if sort == "추천순":
        order = "likes DESC, id DESC"

    if category == "전체":
        query = f"""
        SELECT *
        FROM suggestions
        ORDER BY {order}
        """
        cursor.execute(query)

    else:
        query = f"""
        SELECT *
        FROM suggestions
        WHERE category=?
        ORDER BY {order}
        """
        cursor.execute(query, (category,))

    return cursor.fetchall()


def delete_suggestion(idx):
    cursor.execute(
        "DELETE FROM suggestions WHERE id=?",
        (idx,)
    )
    conn.commit()


def like_suggestion(idx):
    cursor.execute(
        """
        UPDATE suggestions
        SET likes = likes + 1
        WHERE id=?
        """,
        (idx,)
    )
    conn.commit()


# -----------------------------
# 제목
# -----------------------------
st.markdown(
    "<div class='big-title'>📮 학급 건의함</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>익명으로 자유롭게 의견을 남겨보세요!</div>",
    unsafe_allow_html=True
)

# -----------------------------
# 통계
# -----------------------------
cursor.execute(
    "SELECT COUNT(*) FROM suggestions"
)

total = cursor.fetchone()[0]

cursor.execute("""
SELECT category, COUNT(*)
FROM suggestions
GROUP BY category
""")

stats = cursor.fetchall()

col1, col2 = st.columns([1, 2])

with col1:
    st.metric(
        "전체 건의 수",
        total
    )

with col2:
    if stats:
        df = pd.DataFrame(
            stats,
            columns=["카테고리", "개수"]
        )
        st.bar_chart(
            df.set_index("카테고리")
        )

st.divider()

# -----------------------------
# 건의 작성
# -----------------------------
st.subheader("✏️ 건의 작성")

categories = [
    "수업",
    "행사",
    "환경",
    "규칙",
    "기타"
]

with st.form("write_form", clear_on_submit=True):

    category = st.selectbox(
        "건의 종류",
        categories
    )

    content = st.text_area(
        "건의 내용",
        height=120,
        placeholder="예) 체육시간을 조금 더 늘려주세요."
    )

    submitted = st.form_submit_button(
        "📨 건의 등록"
    )

    if submitted:

        if not content.strip():
            st.error("내용을 입력해주세요.")
        else:
            try:
                add_suggestion(
                    category,
                    content
                )

                st.success(
                    "건의가 등록되었습니다!"
                )

                st.rerun()

            except Exception as e:
                st.error(
                    f"오류 발생 : {e}"
                )

st.divider()

# -----------------------------
# 게시판 설정
# -----------------------------
left, right = st.columns(2)

with left:
    selected_category = st.selectbox(
        "카테고리",
        ["전체"] + categories
    )

with right:
    sort_option = st.radio(
        "정렬",
        ["최신순", "추천순"],
        horizontal=True
    )

# -----------------------------
# 게시글 목록
# -----------------------------
posts = get_suggestions(
    selected_category,
    sort_option
)

st.subheader("📋 건의 목록")

if not posts:
    st.info(
        "아직 등록된 건의가 없습니다."
    )

else:

    for post in posts:

        idx = post[0]
        category = post[1]
        content = post[2]
        likes = post[3]
        created_at = post[4]

        with st.container():

            st.markdown(
                f"""
                <div class='card'>
                <h4>📂 {category}</h4>
                <p>{content}</p>
                <small>🕒 {created_at}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns(
                [1, 1, 6]
            )

            with c1:
                if st.button(
                    f"👍 {likes}",
                    key=f"like{idx}"
                ):
                    like_suggestion(idx)
                    st.rerun()

            with c2:
                if st.button(
                    "🗑️ 취소",
                    key=f"delete{idx}"
                ):
                    delete_suggestion(idx)
                    st.rerun()

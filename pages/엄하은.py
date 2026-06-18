import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================
# 페이지 설정
# ==========================
st.set_page_config(
    page_title="학급 건의함",
    page_icon="📮",
    layout="wide"
)

# ==========================
# 스타일
# ==========================
st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.block {
    background:#f8fafc;
    padding:15px;
    border-radius:15px;
    border:1px solid #e2e8f0;
    margin-bottom:10px;
}

.title {
    text-align:center;
    font-size:42px;
    font-weight:bold;
    color:#2563eb;
}

.sub {
    text-align:center;
    color:gray;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# DB 연결
# ==========================
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

# ==========================
# 함수
# ==========================
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


def get_suggestions(category="전체"):

    if category == "전체":
        cursor.execute("""
        SELECT *
        FROM suggestions
        ORDER BY likes DESC, id DESC
        """)
    else:
        cursor.execute("""
        SELECT *
        FROM suggestions
        WHERE category=?
        ORDER BY likes DESC, id DESC
        """,
        (category,))

    return cursor.fetchall()


def delete_suggestion(idx):
    cursor.execute(
        "DELETE FROM suggestions WHERE id=?",
        (idx,)
    )
    conn.commit()


def like_suggestion(idx):
    cursor.execute("""
    UPDATE suggestions
    SET likes = likes + 1
    WHERE id=?
    """,
    (idx,))
    conn.commit()

# ==========================
# 제목
# ==========================
st.markdown(
    "<div class='title'>📮 학급 건의함</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='sub'>우리 반을 더 좋게 만드는 아이디어를 남겨보세요!</div>",
    unsafe_allow_html=True
)

st.divider()

# ==========================
# 메뉴
# ==========================
menu = st.sidebar.radio(
    "메뉴 선택",
    [
        "📝 건의하기",
        "📋 건의 목록",
        "📊 통계"
    ]
)

categories = [
    "수업",
    "행사",
    "환경",
    "규칙",
    "기타"
]

# ==========================
# 건의하기
# ==========================
if menu == "📝 건의하기":

    st.header("📝 건의 작성")

    with st.form(
        "write_form",
        clear_on_submit=True
    ):

        category = st.selectbox(
            "건의 종류",
            categories
        )

        content = st.text_area(
            "건의 내용",
            height=150,
            placeholder="익명으로 건의가 등록됩니다."
        )

        submit = st.form_submit_button(
            "📨 건의 등록"
        )

        if submit:

            if not content.strip():
                st.error(
                    "건의 내용을 입력해주세요."
                )

            else:
                try:
                    add_suggestion(
                        category,
                        content
                    )

                    st.success(
                        "건의가 등록되었습니다!"
                    )

                except Exception as e:
                    st.error(
                        f"오류 : {e}"
                    )

# ==========================
# 건의 목록
# ==========================
elif menu == "📋 건의 목록":

    st.header("📋 건의 목록")

    selected_category = st.selectbox(
        "카테고리 선택",
        ["전체"] + categories
    )

    posts = get_suggestions(
        selected_category
    )

    if not posts:
        st.info(
            "등록된 건의가 없습니다."
        )

    else:

        for post in posts:

            idx = post[0]
            category = post[1]
            content = post[2]
            likes = post[3]
            created = post[4]

            st.markdown(
                f"""
                <div class='block'>
                <h4>📂 {category}</h4>
                <p>{content}</p>
                <small>🕒 {created}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns(
                [1,1,8]
            )

            with col1:
                if st.button(
                    f"👍 {likes}",
                    key=f"like{idx}"
                ):
                    like_suggestion(idx)
                    st.rerun()

            with col2:
                if st.button(
                    "🗑️",
                    key=f"delete{idx}"
                ):
                    delete_suggestion(idx)
                    st.rerun()

# ==========================
# 통계
# ==========================
elif menu == "📊 통계":

    st.header("📊 건의 통계")

    cursor.execute("""
    SELECT category,
           COUNT(*)
    FROM suggestions
    GROUP BY category
    """)

    stats = cursor.fetchall()

    cursor.execute("""
    SELECT COUNT(*)
    FROM suggestions
    """)

    total = cursor.fetchone()[0]

    st.metric(
        "전체 건의 수",
        total
    )

    if stats:

        df = pd.DataFrame(
            stats,
            columns=[
                "카테고리",
                "건수"
            ]
        )

        st.bar_chart(
            df.set_index(
                "카테고리"
            )
        )

    else:
        st.info(
            "통계 데이터가 없습니다."
        )

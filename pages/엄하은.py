import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime

st.set_page_config(
    page_title="학급 건의함",
    page_icon="📮",
    layout="wide"
)

DATA_FILE = "suggestions.csv"


# --------------------------
# 데이터 파일 생성
# --------------------------
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(
        columns=[
            "id",
            "category",
            "content",
            "writer",
            "date",
            "delete_code"
        ]
    )
    df.to_csv(DATA_FILE, index=False)


# --------------------------
# 데이터 불러오기
# --------------------------
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(
            columns=[
                "id",
                "category",
                "content",
                "writer",
                "date",
                "delete_code"
            ]
        )


# --------------------------
# 데이터 저장
# --------------------------
def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# --------------------------
# 제목
# --------------------------
st.title("📮 학급 건의함")
st.caption("익명으로 자유롭게 건의할 수 있습니다.")

menu = st.sidebar.radio(
    "메뉴 선택",
    ["✍️ 건의하기", "📋 건의 게시판"]
)

# ==================================================
# 건의하기 페이지
# ==================================================
if menu == "✍️ 건의하기":

    st.header("건의 작성")

    category = st.selectbox(
        "건의 종류",
        [
            "수업",
            "급식",
            "학급 환경",
            "행사",
            "기타"
        ]
    )

    content = st.text_area(
        "건의 내용을 입력하세요",
        height=200
    )

    anonymous = st.checkbox(
        "익명으로 작성하기",
        value=True
    )

    if anonymous:
        writer = "익명"
    else:
        writer = st.text_input("이름")

    if st.button("건의 등록", use_container_width=True):

        if not content.strip():
            st.error("건의 내용을 입력해주세요.")
        else:

            delete_code = str(uuid.uuid4())[:8]

            new_row = {
                "id": str(uuid.uuid4()),
                "category": category,
                "content": content,
                "writer": writer if writer else "익명",
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "delete_code": delete_code
            }

            df = load_data()

            df = pd.concat(
                [df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            save_data(df)

            st.success("건의가 등록되었습니다!")

            st.info(
                f"""
                삭제코드: **{delete_code}**

                ⚠️ 삭제를 원할 때 필요합니다.
                꼭 저장해두세요.
                """
            )


# ==================================================
# 게시판 페이지
# ==================================================
else:

    st.header("건의 게시판")

    df = load_data()

    if df.empty:
        st.info("등록된 건의가 없습니다.")
        st.stop()

    categories = ["전체"] + sorted(df["category"].unique().tolist())

    selected = st.selectbox(
        "카테고리 선택",
        categories
    )

    if selected != "전체":
        df = df[df["category"] == selected]

    df = df.sort_values(
        by="date",
        ascending=False
    )

    st.write(f"총 {len(df)}개의 건의")

    for idx, row in df.iterrows():

        with st.expander(
            f"[{row['category']}] {row['date']}"
        ):

            st.write("작성자")
            st.info(row["writer"])

            st.write("내용")
            st.write(row["content"])

            st.divider()

if st.button(
    "🗑️ 삭제하기",
    key=f"delete_{row['id']}",
    use_container_width=True
):

    original_df = load_data()

    original_df = original_df[
        original_df["id"] != row["id"]
    ]

    save_data(original_df)

    st.success("삭제되었습니다.")
    st.rerun()

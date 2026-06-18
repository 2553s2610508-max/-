import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="학급 건의함",
    page_icon="📮",
    layout="wide"
)

FILE_NAME = "suggestions.csv"

# ----------------------
# CSV 파일 생성
# ----------------------
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(
        columns=["번호", "종류", "제목", "내용", "작성자", "좋아요"]
    )
    df.to_csv(FILE_NAME, index=False, encoding="utf-8-sig")

# ----------------------
# 데이터 불러오기
# ----------------------
def load_data():
    try:
        return pd.read_csv(FILE_NAME)
    except:
        return pd.DataFrame(
            columns=["번호", "종류", "제목", "내용", "작성자", "좋아요"]
        )

# ----------------------
# 데이터 저장
# ----------------------
def save_data(df):
    df.to_csv(FILE_NAME, index=False, encoding="utf-8-sig")

# ----------------------
# 제목
# ----------------------
st.title("📮 학급 건의함")
st.caption("우리 반을 더 좋은 공간으로 만들기 위한 익명 건의 게시판")

tabs = st.tabs([
    "✍️ 건의 작성",
    "📋 건의 게시판",
    "🔥 인기 건의"
])

# =====================================================
# 건의 작성
# =====================================================
with tabs[0]:

    st.subheader("새 건의 작성")

    category = st.selectbox(
        "건의 종류",
        [
            "수업"
            "교실 환경",
            "행사",
            "학급 규칙",
            "기타"
        ]
    )

    title = st.text_input("제목")

    content = st.text_area(
        "건의 내용",
        height=150
    )

    anonymous = st.checkbox(
        "익명으로 작성하기",
        value=True
    )

    name = "익명"

    if not anonymous:
        name = st.text_input("이름")

    if st.button("건의 등록"):

        if not title.strip():
            st.error("제목을 입력해주세요.")
        elif not content.strip():
            st.error("내용을 입력해주세요.")
        else:

            df = load_data()

            new_id = 1
            if len(df) > 0:
                new_id = int(df["번호"].max()) + 1

            writer = "익명" if anonymous else name

            new_row = {
                "번호": new_id,
                "종류": category,
                "제목": title,
                "내용": content,
                "작성자": writer,
                "좋아요": 0
            }

            df = pd.concat(
                [df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            save_data(df)

            st.success("건의가 등록되었습니다!")

# =====================================================
# 게시판
# =====================================================
with tabs[1]:

    st.subheader("건의 게시판")

    df = load_data()

    if len(df) == 0:
        st.info("등록된 건의가 없습니다.")

    else:

        filter_category = st.selectbox(
            "종류 선택",
            ["전체"] + list(df["종류"].unique())
        )

        if filter_category != "전체":
            df_view = df[df["종류"] == filter_category]
        else:
            df_view = df

        df_view = df_view.sort_values(
            by="번호",
            ascending=False
        )

        for idx, row in df_view.iterrows():

            with st.expander(
                f"[{row['종류']}] {row['제목']}"
            ):

                st.write(row["내용"])

                st.caption(
                    f"작성자 : {row['작성자']}"
                )

                col1, col2 = st.columns([1, 5])

                with col1:
                    if st.button(
                        f"👍 {row['좋아요']}",
                        key=f"like_{row['번호']}"
                    ):
                        df.loc[idx, "좋아요"] += 1
                        save_data(df)
                        st.rerun()

# =====================================================
# 인기 건의
# =====================================================
with tabs[2]:

    st.subheader("🔥 인기 건의 TOP 5")

    df = load_data()

    if len(df) == 0:
        st.info("등록된 건의가 없습니다.")

    else:

        top_df = df.sort_values(
            by="좋아요",
            ascending=False
        ).head(5)

        for _, row in top_df.iterrows():

            st.markdown(
                f"""
### {row['제목']}
📂 {row['종류']}

👍 좋아요 {row['좋아요']}개

{row['내용']}
---
"""
            )

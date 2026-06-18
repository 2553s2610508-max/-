import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="학급 건의함",
    page_icon="📮",
    layout="wide"
)

FILE_NAME = "suggestions.csv"

# ----------------------------------
# 파일 생성
# ----------------------------------
if not os.path.exists(FILE_NAME):
    pd.DataFrame(
        columns=[
            "번호",
            "종류",
            "제목",
            "내용",
            "작성자",
            "비밀번호",
            "좋아요"
        ]
    ).to_csv(FILE_NAME, index=False, encoding="utf-8-sig")

# ----------------------------------
# 데이터 불러오기
# ----------------------------------
def load_data():
    try:
        return pd.read_csv(FILE_NAME)
    except:
        return pd.DataFrame(
            columns=[
                "번호",
                "종류",
                "제목",
                "내용",
                "작성자",
                "비밀번호",
                "좋아요"
            ]
        )

# ----------------------------------
# 데이터 저장
# ----------------------------------
def save_data(df):
    df.to_csv(FILE_NAME, index=False, encoding="utf-8-sig")

# ----------------------------------
# 제목
# ----------------------------------
st.title("📮 학급 건의함")
st.caption("우리 반을 더 좋은 공간으로 만들기 위한 익명 건의 게시판")

tabs = st.tabs([
    "✍️ 건의 작성",
    "📋 게시판",
    "🔥 인기 건의",
    "❌ 건의 취소"
])

# ==================================================
# 건의 작성
# ==================================================
with tabs[0]:

    st.subheader("새 건의 작성")

    category = st.selectbox(
        "건의 종류",
        [
            "수업",
            "급식",
            "교실 환경",
            "학급 행사",
            "동아리",
            "학급 규칙",
            "시험 및 평가",
            "청소",
            "자리 배치",
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

    if anonymous:
        writer = "익명"
    else:
        writer = st.text_input("이름")

    delete_pw = st.text_input(
        "취소용 비밀번호",
        type="password",
        help="나중에 건의를 취소할 때 사용됩니다."
    )

    if st.button("건의 등록"):

        if not title.strip():
            st.error("제목을 입력하세요.")
        elif not content.strip():
            st.error("내용을 입력하세요.")
        elif not delete_pw.strip():
            st.error("취소용 비밀번호를 입력하세요.")
        else:

            df = load_data()

            if len(df) == 0:
                new_id = 1
            else:
                new_id = int(df["번호"].max()) + 1

            new_row = {
                "번호": new_id,
                "종류": category,
                "제목": title,
                "내용": content,
                "작성자": writer,
                "비밀번호": delete_pw,
                "좋아요": 0
            }

            df = pd.concat(
                [df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            save_data(df)

            st.success(
                f"건의가 등록되었습니다! (건의번호: {new_id})"
            )

# ==================================================
# 게시판
# ==================================================
with tabs[1]:

    df = load_data()

    if len(df) == 0:
        st.info("등록된 건의가 없습니다.")

    else:

        category_filter = st.selectbox(
            "카테고리 선택",
            ["전체"] + list(df["종류"].unique())
        )

        if category_filter == "전체":
            view_df = df
        else:
            view_df = df[df["종류"] == category_filter]

        view_df = view_df.sort_values(
            by="번호",
            ascending=False
        )

        for idx, row in view_df.iterrows():

            with st.expander(
                f"[{row['종류']}] {row['제목']}"
            ):

                st.write(row["내용"])

                st.caption(
                    f"작성자 : {row['작성자']}"
                )

                if st.button(
                    f"👍 {row['좋아요']}",
                    key=f"like_{row['번호']}"
                ):

                    original_idx = df[
                        df["번호"] == row["번호"]
                    ].index[0]

                    df.loc[
                        original_idx,
                        "좋아요"
                    ] += 1

                    save_data(df)
                    st.rerun()

# ==================================================
# 인기 건의
# ==================================================
with tabs[2]:

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

# ==================================================
# 건의 취소
# ==================================================
with tabs[3]:

    st.subheader("❌ 내가 작성한 건의 취소")

    suggestion_id = st.number_input(
        "건의번호",
        min_value=1,
        step=1
    )

    password = st.text_input(
        "취소용 비밀번호",
        type="password"
    )

    if st.button("건의 취소"):

        df = load_data()

        target = df[
            (df["번호"] == suggestion_id)
            & (df["비밀번호"] == password)
        ]

        if len(target) == 0:

            st.error(
                "건의번호 또는 비밀번호가 올바르지 않습니다."
            )

        else:

            df = df[
                ~(
                    (df["번호"] == suggestion_id)
                    & (df["비밀번호"] == password)
                )
            ]

            save_data(df)

            st.success(
                "건의가 정상적으로 취소되었습니다."
            )
            st.rerun()

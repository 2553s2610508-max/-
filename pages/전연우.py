import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="시험 일정 도우미",
    page_icon="📚",
    layout="wide"
)

st.title("📚시험 일정도우미")
st.subheader("수행평가와 시험 일정을 한눈에 관리하세요!")

# 세션 상태 초기화
if "schedule" not in st.session_state:
    st.session_state.schedule = pd.DataFrame({
        "구분": ["수행평가", "시험"],
        "과목": ["국어", "수학"],
        "날짜": [pd.to_datetime("2026-06-25"), pd.to_datetime("2026-07-01")],
        "내용": ["독서 발표", "중간고사"]
    })

# 일정 추가
st.sidebar.header("➕ 일정 추가")

schedule_type = st.sidebar.selectbox(
    "구분",
    ["수행평가", "시험"]
)

subject = st.sidebar.text_input("과목")

schedule_date = st.sidebar.date_input(
    "날짜",
    value=date.today()
)

description = st.sidebar.text_input("내용")

if st.sidebar.button("일정 추가"):
    if subject.strip() and description.strip():
        new_row = pd.DataFrame({
            "구분": [schedule_type],
            "과목": [subject],
            "날짜": [pd.to_datetime(schedule_date)],
            "내용": [description]
        })

        st.session_state.schedule = pd.concat(
            [st.session_state.schedule, new_row],
            ignore_index=True
        )

        st.sidebar.success("일정이 추가되었습니다!")
    else:
        st.sidebar.error("과목과 내용을 입력해주세요.")

# 데이터 복사
df = st.session_state.schedule.copy()

# 정렬
df = df.sort_values("날짜")

# D-Day 계산
today = pd.Timestamp.today().normalize()
df["D-Day"] = (df["날짜"] - today).dt.days

def dday_text(days):
    if days == 0:
        return "🔥 D-Day"
    elif days > 0:
        return f"D-{days}"
    else:
        return f"D+{abs(days)}"

df["D-Day"] = df["D-Day"].apply(dday_text)

# 필터
st.markdown("### 🔍 일정 필터")

filter_option = st.radio(
    "보기",
    ["전체", "시험", "수행평가"],
    horizontal=True
)

filtered_df = df.copy()

if filter_option != "전체":
    filtered_df = filtered_df[filtered_df["구분"] == filter_option]

# 통계
exam_count = len(df[df["구분"] == "시험"])
performance_count = len(df[df["구분"] == "수행평가"])

col1, col2 = st.columns(2)

with col1:
    st.metric("📝 수행평가", performance_count)

with col2:
    st.metric("📖 시험", exam_count)

# 일정 표시
st.markdown("### 📅 전체 일정")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# 다가오는 일정
st.markdown("### 🚨 가장 가까운 일정")

future_df = df[df["날짜"] >= today]

if not future_df.empty:
    nearest = future_df.iloc[0]

    st.info(
        f"""
        **{nearest['과목']}**
        
        - 구분: {nearest['구분']}
        - 날짜: {nearest['날짜'].strftime('%Y-%m-%d')}
        - 내용: {nearest['내용']}
        - {nearest['D-Day']}
        """
    )
else:
    st.success("예정된 일정이 없습니다.")

# CSV 다운로드
csv = filtered_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="⬇️ 일정 CSV 다운로드",
    data=csv,
    file_name="class_schedule.csv",
    mime="text/csv"
)

st.markdown("---")
st.caption("반장 도우미 | 수행평가·시험 일정 관리 앱")
# ==========================
# 일정 수정 / 삭제
# ==========================
st.markdown("## ⚙️ 일정 관리")
if not st.session_state.schedule.empty:
    manage_options = [
        f"{row['과목']} | {row['내용']} | {row['날짜'].strftime('%Y-%m-%d')}"
        for _, row in st.session_state.schedule.iterrows()
    ]
    selected_item = st.selectbox(
        "관리할 일정을 선택하세요",
        manage_options
    )
    selected_index = manage_options.index(selected_item)
    selected_row = st.session_state.schedule.iloc[selected_index]
    tab1, tab2 = st.tabs(["✏️ 수정", "🗑️ 삭제"])
    # -------------------
    # 수정 기능
    # -------------------
    with tab1:
        st.write("선택한 일정 수정")
        new_type = st.selectbox(
            "구분",
            ["수행평가", "시험"],
            index=0 if selected_row["구분"] == "수행평가" else 1,
            key="edit_type"
        )
        new_subject = st.text_input(
            "과목",
            value=selected_row["과목"],
            key="edit_subject"
        )
        new_date = st.date_input(
            "날짜",
            value=selected_row["날짜"].date(),
            key="edit_date"
        )
        new_content = st.text_input(
            "내용",
            value=selected_row["내용"],
            key="edit_content"
        )
        if st.button("수정 저장"):
            if new_subject.strip() and new_content.strip():
                st.session_state.schedule.loc[selected_index, "구분"] = new_type
                st.session_state.schedule.loc[selected_index, "과목"] = new_subject
                st.session_state.schedule.loc[selected_index, "날짜"] = pd.to_datetime(new_date)
                st.session_state.schedule.loc[selected_index, "내용"] = new_content
                st.success("수정이 완료되었습니다.")
                st.rerun()
            else:
                st.error("과목과 내용을 입력해주세요.")
    # -------------------
    # 삭제 기능
    # -------------------
    with tab2:
        st.warning("삭제된 일정은 복구되지 않습니다.")
        if st.button("선택한 일정 삭제"):
            st.session_state.schedule = (
                st.session_state.schedule
                .drop(st.session_state.schedule.index[selected_index])
                .reset_index(drop=True)
            )
            st.success("일정이 삭제되었습니다.")
            st.rerun()
else:
    st.info("등록된 일정이 없습니다.")

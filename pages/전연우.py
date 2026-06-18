import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="반장 도우미",
    page_icon="📚",
    layout="wide"
)

st.title("📚 반장 도우미")
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

import streamlit as st
import random
from datetime import date

st.set_page_config(
    page_title="반장 도우미",
    page_icon="🏫",
    layout="wide"
)

st.title("🏫 반장 도우미")
st.caption("우리 반을 더 편리하게 관리하는 통합 서비스")

# -----------------------------
# 세션 상태
# -----------------------------
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

if "events" not in st.session_state:
    st.session_state.events = []

# -----------------------------
# 메인 소개
# -----------------------------
st.info(
    """
    👋 안녕하세요!

    이 페이지는 우리 반 친구들을 위해 만들어진 반장 도우미 입니다

    아래 기능들을 사용할 수 있습니다.

    ✅ 단합대회 일정 조율

    ✅ 건의함

    ✅ 시험·수행평가 캘린더

    ✅ 공정한 자리 바꾸기
    """
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🎉 단합대회",
        "📮 건의함",
        "📅 학급 캘린더",
        "🪑 자리 바꾸기"
    ]
)

# ====================================================
# 단합대회
# ====================================================
with tab1:

    st.header("🎉 단합대회 일정 조율")

    st.write(
        """
        단합대회 후보 날짜를 정해두고
        친구들과 상의하여 일정을 결정할 수 있습니다.
        """
    )

    event_name = st.text_input(
        "행사 이름",
        key="event_name"
    )

    event_date = st.date_input(
        "후보 날짜",
        value=date.today(),
        key="event_date"
    )

    if st.button("일정 추가"):

        try:
            if event_name.strip():

                st.session_state.events.append(
                    {
                        "name": event_name,
                        "date": event_date
                    }
                )

                st.success("일정 추가 완료")

            else:
                st.warning("행사 이름을 입력하세요.")

        except Exception as e:
            st.error(f"오류 발생: {e}")

    if st.session_state.events:

        st.subheader("등록된 일정")

        for idx, event in enumerate(
            st.session_state.events,
            start=1
        ):
            st.write(
                f"{idx}. {event['name']} - {event['date']}"
            )

# ====================================================
# 건의함
# ====================================================
with tab2:

    st.header("📮 건의함")

    st.write(
        """
        우리 반에 필요한 물품이나
        바뀌었으면 하는 점을 자유롭게 적어주세요.
        """
    )

    suggestion = st.text_area(
        "건의 내용"
    )

    if st.button("건의 등록"):

        try:

            if suggestion.strip():

                st.session_state.suggestions.append(
                    suggestion
                )

                st.success("건의가 등록되었습니다.")

            else:
                st.warning("내용을 입력하세요.")

        except Exception as e:
            st.error(f"오류 발생: {e}")

    if st.session_state.suggestions:

        st.subheader("등록된 건의")

        for idx, item in enumerate(
            st.session_state.suggestions,
            start=1
        ):
            st.write(f"{idx}. {item}")

# ====================================================
# 캘린더
# ====================================================
with tab3:

    st.header("📅 시험 · 수행평가 캘린더")

    st.write(
        """
        시험 일정과 수행평가 일정을 기록할 수 있습니다.
        """
    )

    title = st.text_input(
        "일정 이름",
        key="calendar_title"
    )

    schedule_date = st.date_input(
        "날짜",
        value=date.today(),
        key="calendar_date"
    )

    if st.button("일정 등록"):

        try:

            if title.strip():

                st.session_state.events.append(
                    {
                        "name": title,
                        "date": schedule_date
                    }
                )

                st.success("등록 완료")

            else:
                st.warning("일정 이름을 입력하세요.")

        except Exception as e:
            st.error(f"오류 발생: {e}")

    if st.session_state.events:

        st.subheader("예정된 일정")

        sorted_events = sorted(
            st.session_state.events,
            key=lambda x: x["date"]
        )

        for event in sorted_events:

            st.write(
                f"📌 {event['date']} | {event['name']}"
            )

# ====================================================
# 자리 바꾸기
# ====================================================
with tab4:

    st.header("🪑 공정한 자리 바꾸기")

    st.write(
        """
        학생 이름을 입력하면
        무작위로 새로운 순서를 만들어 줍니다.
        """
    )

    students = st.text_area(
        "학생 이름 입력 (한 줄에 한 명)"
    )

    if st.button("자리 배치 생성"):

        try:

            names = [
                n.strip()
                for n in students.split("\n")
                if n.strip()
            ]

            if len(names) < 2:
                st.warning(
                    "2명 이상 입력하세요."
                )

            else:

                random.shuffle(names)

                st.success(
                    "새로운 자리 순서가 생성되었습니다."
                )

                for idx, student in enumerate(
                    names,
                    start=1
                ):
                    st.write(
                        f"{idx}번 자리 → {student}"
                    )

        except Exception as e:
            st.error(f"오류 발생: {e}")

st.divider()

st.caption(
    "반장 도우미 | 우리 반을 위한 간단한 관리 서비스"
)


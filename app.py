import streamlit as st
import random

st.set_page_config(
    page_title="반장 발표 도우미 Pro",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 반장 발표 도우미 Pro")

st.markdown(
    """
친구들이 만든 작품을
반장이 앞에서 간단히 소개할 때 사용하는 앱입니다.

- 작품 요약
- 발표 대본 생성
- 예상 질문 생성
- 발표 순서 관리
"""
)

# -------------------
# 세션 상태
# -------------------

if "order_list" not in st.session_state:
    st.session_state.order_list = []

# -------------------
# 메뉴
# -------------------

menu = st.sidebar.radio(
    "메뉴",
    [
        "작품 소개 만들기",
        "발표 순서",
        "랜덤 발표자",
        "사용 방법"
    ]
)

# -------------------
# 사용 방법
# -------------------

if menu == "사용 방법":

    st.header("📖 사용 방법")

    st.write("1. 작품 제목 입력")
    st.write("2. 만든 학생 입력")
    st.write("3. 작품 설명 입력")
    st.write("4. 소개 생성 버튼 클릭")
    st.write("5. 생성된 내용을 그대로 읽으면 됨")

# -------------------
# 작품 소개
# -------------------

elif menu == "작품 소개 만들기":

    st.header("📝 작품 소개 생성")

    title = st.text_input("작품 제목")

    creator = st.text_input("만든 학생")

    description = st.text_area(
        "작품 설명",
        height=200,
        placeholder="작품 내용을 간단히 입력하세요."
    )

    if st.button("소개 생성"):

        try:

            if not title.strip():
                st.warning("작품 제목을 입력하세요.")
                st.stop()

            if not creator.strip():
                st.warning("만든 학생을 입력하세요.")
                st.stop()

            if not description.strip():
                st.warning("작품 설명을 입력하세요.")
                st.stop()

            short_script = f"""
안녕하세요.

이번 작품은 '{title}'입니다.

{creator} 학생이 제작했으며,
{description[:80]}...

이상으로 소개를 마치겠습니다.
"""

            long_script = f"""
안녕하세요.

지금부터 '{title}' 작품을 소개하겠습니다.

이 작품은 {creator} 학생이 제작했습니다.

작품 설명:
{description}

학생의 아이디어와 노력이 담긴 작품이며,
주제를 잘 표현하고 있습니다.

이상으로 소개를 마치겠습니다.
"""

            keywords = []

            for word in description.split():

                word = word.strip(".,!?()[]{}")

                if len(word) >= 3:
                    keywords.append(word)

            keywords = list(dict.fromkeys(keywords))

            st.success("생성 완료")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("⚡ 10초 소개")

                st.text_area(
                    "",
                    short_script,
                    height=180
                )

            with col2:
                st.subheader("🎙️ 30초 소개")

                st.text_area(
                    "",
                    long_script,
                    height=180
                )

            st.subheader("🔑 핵심 키워드")

            if keywords:
                st.write(", ".join(keywords[:10]))
            else:
                st.write("키워드 추출 결과 없음")

            st.subheader("❓ 예상 질문")

            st.write("• 이 작품을 만들게 된 이유는 무엇인가요?")
            st.write("• 가장 어려웠던 점은 무엇인가요?")
            st.write("• 가장 신경 쓴 부분은 어디인가요?")
            st.write("• 개선한다면 무엇을 바꾸고 싶나요?")

        except Exception as e:
            st.error(f"오류 발생: {e}")

# -------------------
# 발표 순서
# -------------------

elif menu == "발표 순서":

    st.header("📋 발표 순서 관리")

    name = st.text_input("학생 이름")

    if st.button("순서 추가"):

        if name.strip():
            st.session_state.order_list.append(name.strip())
            st.success("추가 완료")
        else:
            st.warning("이름을 입력하세요.")

    if st.session_state.order_list:

        st.subheader("현재 발표 순서")

        for idx, student in enumerate(
            st.session_state.order_list,
            start=1
        ):
            st.write(f"{idx}. {student}")

        if st.button("전체 삭제"):
            st.session_state.order_list = []
            st.rerun()

# -------------------
# 랜덤 발표자
# -------------------

elif menu == "랜덤 발표자":

    st.header("🎲 랜덤 발표자 뽑기")

    names = st.text_area(
        "이름 입력 (한 줄에 한 명)"
    )

    if st.button("발표자 선택"):

        try:

            people = [
                n.strip()
                for n in names.split("\n")
                if n.strip()
            ]

            if len(people) == 0:
                st.warning("이름을 입력하세요.")
            else:
                selected = random.choice(people)

                st.success(
                    f"오늘의 발표자: {selected}"
                )

        except Exception as e:
            st.error(f"오류 발생: {e}")

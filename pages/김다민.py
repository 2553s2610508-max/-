import streamlit as st
import pandas as pd
import random
import math

st.set_page_config(
    page_title="우리 반 스마트 자리배치 도우미",
    layout="wide"
)

st.title("🏫 우리 반 스마트 자리배치 도우미")

st.markdown("""
시력, 키, 친구 관계를 고려하여
학생들에게 가장 적절한 자리 배치를 추천합니다.
""")

# -------------------------
# 학생 수
# -------------------------

student_count = st.number_input(
    "학생 수",
    min_value=1,
    max_value=40,
    value=10
)

st.divider()

students = []

st.subheader("학생 정보 입력")

for i in range(student_count):
    with st.expander(f"학생 {i+1}"):

        name = st.text_input(
            f"이름_{i}",
            value=f"학생{i+1}"
        )

        height = st.number_input(
            f"키(cm)_{i}",
            min_value=100,
            max_value=220,
            value=160
        )

        eyesight = st.number_input(
            f"시력_{i}",
            min_value=0.1,
            max_value=2.0,
            value=1.0,
            step=0.1
        )

        friend = st.text_input(
            f"가까이 앉고 싶은 친구 이름_{i}",
            value=""
        )

        avoid = st.text_input(
            f"떨어지고 싶은 친구 이름_{i}",
            value=""
        )

        students.append({
            "name": name.strip(),
            "height": height,
            "eyesight": eyesight,
            "friend": friend.strip(),
            "avoid": avoid.strip()
        })

st.divider()

cols = st.columns(2)

rows = cols[0].number_input(
    "교실 행 수",
    min_value=1,
    max_value=10,
    value=3
)

seats_per_row = cols[1].number_input(
    "한 행의 자리 수",
    min_value=1,
    max_value=10,
    value=4
)

total_seats = rows * seats_per_row

if st.button("🎯 자동 자리 배치 시작"):

    try:

        if student_count > total_seats:
            st.error(
                "학생 수가 좌석 수보다 많습니다."
            )
            st.stop()

        # -------------------------
        # 시력 + 키 기반 점수
        # -------------------------

        scored_students = []

        for s in students:

            eyesight_score = (2.0 - s["eyesight"]) * 100
            height_score = s["height"] * 0.3

            score = eyesight_score - height_score

            scored_students.append(
                {
                    **s,
                    "score": score
                }
            )

        scored_students.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        seats = []

        for r in range(rows):
            for c in range(seats_per_row):
                seats.append((r, c))

        assignment = {}

        for student, seat in zip(scored_students, seats):
            assignment[student["name"]] = seat

        # -------------------------
        # 친구 관계 개선
        # -------------------------

        for _ in range(100):

            improved = False

            for s in scored_students:

                name = s["name"]

                if not s["friend"]:
                    continue

                if (
                    s["friend"] not in assignment
                    or name not in assignment
                ):
                    continue

                my_seat = assignment[name]
                friend_seat = assignment[s["friend"]]

                dist = abs(my_seat[0]-friend_seat[0]) + abs(my_seat[1]-friend_seat[1])

                if dist > 2:

                    friend_name = s["friend"]

                    swap_target = None

                    best_dist = dist

                    for other_name, other_seat in assignment.items():

                        if other_name == friend_name:
                            continue

                        new_dist = abs(
                            my_seat[0]-other_seat[0]
                        ) + abs(
                            my_seat[1]-other_seat[1]
                        )

                        if new_dist < best_dist:
                            best_dist = new_dist
                            swap_target = other_name

                    if swap_target:

                        assignment[swap_target], assignment[friend_name] = (
                            assignment[friend_name],
                            assignment[swap_target]
                        )

                        improved = True

            if not improved:
                break

        # -------------------------
        # 결과 표
        # -------------------------

        result = []

        for name, seat in assignment.items():

            result.append({
                "이름": name,
                "행": seat[0] + 1,
                "열": seat[1] + 1
            })

        result_df = pd.DataFrame(result)

        st.success("자리 배치 완료!")

        st.subheader("📋 자리 배치 결과")

        st.dataframe(
            result_df.sort_values(["행", "열"]),
            use_container_width=True
        )

        # -------------------------
        # 교실 시각화
        # -------------------------

        st.subheader("🖥️ 교실 배치도")

        seat_map = [
            ["빈자리" for _ in range(seats_per_row)]
            for _ in range(rows)
        ]

        for name, seat in assignment.items():
            seat_map[seat[0]][seat[1]] = name

        st.markdown("### 📚 칠판")

        display_df = pd.DataFrame(seat_map)

        st.table(display_df)

        # -------------------------
        # CSV 다운로드
        # -------------------------

        csv = result_df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ 결과 CSV 다운로드",
            csv,
            file_name="seat_arrangement.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(
            f"오류가 발생했습니다: {e}"
        )

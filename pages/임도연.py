1. 앱 기획 설명
화면 구성 (Sidebar & Main)

사이드바: 우리 반 명단 입력 및 단합대회 참가비 납부 현황 체크리스트 (5번 기능)

메인 탭 1 [📅 1단계: 일정 조율]: 안되는 요일을 선택하면, 가장 많은 학생이 참여할 수 있는 최적의 요일을 자동으로 계산해 추천 (1번 기능)

메인 탭 2 [🍔 2단계: 음식 및 활동 투표]: 학생들이 자유롭게 낸 의견 중 가장 많이 나온 상위 항목을 자동 추출하여 각각 최대 5개, 최대 3개로 투표 항목을 자동 생성. 1인당 최대 2표 중복 투표 가능 (2, 3번 기능 + 추가 요청사항)

메인 탭 3 [🎬 3단계: 세부 활동 정하기]: 2단계에서 결정된 활동(예: 영화, 게임 등)에 맞춰 세부 의견을 모으고 최대 3개 항목으로 최종 투표 (4번 기능)

2. app.py (전체 코드)
Python
import streamlit as st
import pandas as pd
from collections import Counter

# 페이지 설정
st.set_page_config(page_title="반장 도우미 - 단합대회 기획", page_icon="🎉", layout="wide")

# --- 세션 상태(Session State) 초기화 ---
if "students" not in st.session_state:
    st.session_state.students = ["김유민", "강석현", "강세인", "김기웅", "김다민", "김대현", "김민서", "김솔비", "김용준", "박강이", " 박정후", "박준영", "박현욱", "송유림", "송은호", "송지우", "심예원", "안시윤", "엄하은", "여서현", "오승준", "우정은", "윤희승", "이다은", "이승민", "이예나", "이하준", "이현우", "임도연", "임선웅", "임지선", "전연우", "정선아", "함형민", "황시우"]
if "paid_status" not in st.session_state:
    st.session_state.paid_status = {name: False for name in st.session_state.students}
if "unavailable_days" not in st.session_state:
    st.session_state.unavailable_days = {}
if "food_opinions" not in st.session_state:
    st.session_state.food_opinions = []
if "activity_opinions" not in st.session_state:
    st.session_state.activity_opinions = []
if "detail_opinions" not in st.session_state:
    st.session_state.detail_opinions = []
if "votes_food" not in st.session_state:
    st.session_state.votes_food = {}
if "votes_activity" not in st.session_state:
    st.session_state.votes_activity = {}
if "votes_detail" not in st.session_state:
    st.session_state.votes_detail = {}

# 제목
st.title("🎉 우리 반 단합대회 정하기")
st.caption("우리 반 단합대회를 이 앱으로 한번에!!")
st.markdown("---")

# --- 사이드바: 학생 관리 및 회비 체크 ---
with st.sidebar:
    st.header("👥 우리 반 멤버 및 회비 관리")
    
    # 학생 추가 기능
    new_student = st.text_input("새 학생 이름 추가:", placeholder="홍길동")
    if st.button("추가") and new_student:
        if new_student not in st.session_state.students:
            st.session_state.students.append(new_student)
            st.session_state.paid_status[new_student] = False
            st.rerun()
            
    st.subheader("💰 회비 납부 현황 (5번 기능)")
    st.info("돈을 걷은 학생의 체크박스를 선택하세요.")
    
    # 체크박스로 납부 현황 표시
    for student in st.session_state.students:
        st.session_state.paid_status[student] = st.checkbox(
            f"{student}", value=st.session_state.paid_status.get(student, False), key=f"pay_{student}"
        )
        
    # 정산 통계
    paid_count = sum(st.session_state.paid_status.values())
    total_count = len(st.session_state.students)
    st.metric(label="회비 납부율", value=f"{paid_count} / {total_count}", delta=f"{total_count - paid_count}명 남음")


# --- 메인 화면 탭 구성 ---
tab1, tab2, tab3 = st.tabs(["📅 1단계: 일정 조율", "🍔 2단계: 음식/활동 투표", "🎬 3단계: 세부사항 결정"])

# --- TAB 1: 일정 조율 (1번 기능) ---
with tab1:
    st.header("🗓️ 안되는 날 제외하고 일정 자동 조율하기")
    st.write("각 학생들이 **안되는 요일**을 선택하면, 가장 많이 참여할 수 있는 요일을 자동으로 계산합니다.")
    
    days_of_week = ["월요일", "화요일", "수요일", "목요일", "금요일"]
    
    # 의견 입력 폼
    with st.form("day_form"):
        select_student = st.selectbox("이름 선택:", st.session_state.students, key="day_student")
        bad_days = st.multiselect("안되는 요일을 모두 고르세요:", days_of_week)
        submit_day = st.form_submit_button("의견 제출")
        
        if submit_day:
            st.session_state.unavailable_days[select_student] = bad_days
            st.success(f"{select_student} 너의 의견이 반영됐어!")

    # 결과 현황 분석
    st.subheader("📊 일정 조율 결과")
    if st.session_state.unavailable_days:
        # 요일별 안되는 인원 계산
        impossible_counts = {day: 0 for day in days_of_week}
        for s, days in st.session_state.unavailable_days.items():
            for d in days:
                impossible_counts[d] += 1
                
        # 가능한 인원 계산 (총원 - 안되는 인원)
        possible_counts = {day: total_count - impossible_counts[day] for day in days_of_week}
        
        # 데이터프레임 시각화
        df_days = pd.DataFrame({
            "요일": days_of_week,
            "참여 가능 인원(명)": [possible_counts[d] for d in days_of_week],
            "불가능한 인원(명)": [impossible_counts[d] for d in days_of_week]
        })
        st.dataframe(df_days.set_index("요일"), use_container_width=True)
        
        # 최적의 요일 추천
        max_possible = max(possible_counts.values())
        best_days = [d for d, v in possible_counts.items() if v == max_possible]
        
        st.success(f"💡 **추천 요일:** 현재 가장 많이 참여할 수 있는 요일은 **{', '.join(best_days)}** 입니다! (최대 {max_possible}명 참여 가능)")
    else:
        st.info("아직 제출된 일정 의견이 없습니다.")


# --- TAB 2: 음식 및 활동 투표 (2, 3번 기능) ---
with tab2:
    st.header("🍔 음식 & 🎉 활동 의견 취합 및 투표")
    
    col1, col2 = st.columns(2)
    
    # 의견 입력 구역
    with col1:
        st.subheader("✏️ 의견 내기")
        with st.form("opinion_form"):
            food_input = st.text_input("먹고 싶은 음식 적기:", placeholder="예: 피자, 치킨, 떡볶이")
            act_input = st.text_input("하고 싶은 활동 적기:", placeholder="예: 영화보기, 마피아하기")
            submit_op = st.form_submit_button("의견 제출하기")
            
            if submit_op:
                if food_input: st.session_state.food_opinions.append(food_input.strip())
                if act_input: st.session_state.activity_opinions.append(act_input.strip())
                st.success("의견 받았어!")
                st.rerun()

    with col2:
        st.subheader("📝 취합된 날것의 의견 리스트")
        st.write(f"**제출된 음식들:** {', '.join(st.session_state.food_opinions) if st.session_state.food_opinions else '없음'}")
        st.write(f"**제출된 활동들:** {', '.join(st.session_state.activity_opinions) if st.session_state.activity_opinions else '없음'}")

    st.markdown("---")
    
    # 자동 항목 선정 및 투표 구역
    st.subheader("🗳️ 실시간 투표 (자동 상위 항목 추출)")
    st.caption("💡 아이들이 많이 적어낸 순서대로 자동 정렬되어 투표 항목이 완성됩니다! (1인당 최대 2표 중복 가능)")
    
    v_col1, v_col2 = st.columns(2)
    
    # 2. 음식 투표 (최대 5개 항목 추출)
    with v_col1:
        st.markdown("### 🍕 음식 투표 (최대 5개 항목)")
        if st.session_state.food_opinions:
            # 빈도수 계산 후 상위 5개 추출
            top_foods = [item for item, _ in Counter(st.session_state.food_opinions).most_common(5)]
            
            st.write(f"🤖 **자동 선정된 후보:** {', '.join(top_foods)}")
            
            # 투표 기능 (인당 최대 2표)
            voted_foods = st.multiselect("음식을 선택하세요 (최대 2개):", top_foods, key="food_vote_select")
            if st.button("음식 투표 제출"):
                if len(voted_foods) > 2:
                    st.error("❌ 최대 2개까지만 선택 가능합니다!")
                elif len(voted_foods) == 0:
                    st.warning("⚠️ 항목을 선택해 주세요.")
                else:
                    # 기존 투표에 반영 (간이 누적 방식)
                    for vf in voted_foods:
                        st.session_state.votes_food[vf] = st.session_state.votes_food.get(vf, 0) + 1
                    st.success("음식 투표 성공!")
            
            # 결과 출력
            st.write("**현재 음식 투표 결과:**")
            st.bar_chart(pd.DataFrame.from_dict(st.session_state.votes_food, orient='index', columns=['표 수']))
        else:
            st.info("음식 의견이 등록되면 투표가 생성됩니다.")

    # 3. 활동 투표 (최대 3개 항목 추출)
    with v_col2:
        st.markdown("### 🎯 활동 투표 (최대 3개)")
        if st.session_state.activity_opinions:
            # 빈도수 계산 후 상위 3개 추출
            top_acts = [item for item, _ in Counter(st.session_state.activity_opinions).most_common(3)]
            
            st.write(f"🤖 **자동 선정된 후보:** {', '.join(top_acts)}")
            
            # 투표 기능 (인당 최대 2표)
            voted_acts = st.multiselect("활동을 선택하세요 (최대 2개):", top_acts, key="act_vote_select")
            if st.button("활동 투표 제출"):
                if len(voted_acts) > 2:
                    st.error("❌ 최대 2개까지만 선택 가능합니다!")
                elif len(voted_acts) == 0:
                    st.warning("⚠️ 항목을 선택해 주세요.")
                else:
                    for va in voted_acts:
                        st.session_state.votes_activity[va] = st.session_state.votes_activity.get(va, 0) + 1
                    st.success("활동 투표 성공!")
            
            # 결과 출력
            st.write("**현재 활동 투표 결과:**")
            st.bar_chart(pd.DataFrame.from_dict(st.session_state.votes_activity, orient='index', columns=['표 수']))
        else:
            st.info("활동 의견이 등록되면 투표가 생성됩니다.")


# --- TAB 3: 세부 사항 결정 (4번 기능) ---
with tab3:
    st.header("🎬 3단계: 선정된 활동의 세부 사항 결정")
    st.write("2단계에서 결정된 1등 활동에 대한 구체적인 의견을 모으고 최종 투표를 진행하는 곳입니다.")
    
    # 현재 가장 표를 많이 받은 활동 확인
    current_best_act = "선정된 활동"
    if st.session_state.votes_activity:
        current_best_act = max(st.session_state.votes_activity, key=st.session_state.votes_activity.get)
        st.success(f"👑 현재 1위 활동: **[{current_best_act}]**")
    else:
        st.warning("⚠️ 2단계에서 활동 투표가 먼저 진행되어야 연동이 매끄럽습니다. (기본값 설정 후 진행 가능)")
    
    # 세부 의견 입력
    st.subheader(f"💬 '{current_best_act}'에 대한 구체적인 의견 모으기")
    st.caption("예: 영화라면 영화 제목, 게임이라면 게임 종목 등")
    
    with st.form("detail_form"):
        detail_input = st.text_input(f"'{current_best_act}' 관련 세부 아이디어:", placeholder="예: 어벤져스, 마피아게임 등")
        submit_detail = st.form_submit_button("세부 의견 제출")
        if submit_detail and detail_input:
            st.session_state.detail_opinions.append(detail_input.strip())
            st.success("세부 의견 등록 완료!")
            st.rerun()
            
    st.write(f"**현재 모인 세부 의견:** {', '.join(st.session_state.detail_opinions) if st.session_state.detail_opinions else '없음'}")
    
    st.markdown("---")
    
    # 4. 세부 항목 투표 (최대 3개 자동 추출 및 1인 최대 2표)
    st.subheader(f"🏆 '{current_best_act}' 최종 세부 항목 투표 (최대 3개)")
    
    if st.session_state.detail_opinions:
        top_details = [item for item, _ in Counter(st.session_state.detail_opinions).most_common(3)]
        st.write(f"🤖 **자동 선정된 세부 후보:** {', '.join(top_details)}")
        
        voted_details = st.multiselect("원하는 세부 항목을 선택하세요 (최대 2개):", top_details, key="detail_vote_select")
        if st.button("세부 투표 제출"):
            if len(voted_details) > 2:
                st.error("❌ 최대 2개까지만 선택 가능합니다!")
            elif len(voted_details) == 0:
                st.warning("⚠️ 항목을 선택해 주세요.")
            else:
                for vd in voted_details:
                    st.session_state.votes_detail[vd] = st.session_state.votes_detail.get(vd, 0) + 1
                st.success("세부 투표 반영 완료!")
                
        # 결과 그래프
        st.write("**최종 투표 결과:**")
        if st.session_state.votes_detail:
            st.bar_chart(pd.DataFrame.from_dict(st.session_state.votes_detail, orient='index', columns=['표 수']))
    else:
        st.info("세부 의견이 입력되면 투표 창이 활성화됩니다.")

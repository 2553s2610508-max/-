import streamlit as st
import pandas as pd
from collections import Counter

# 페이지 기본 설정
st.set_page_config(page_title="반장 도우미", page_icon="🎉", layout="wide")

# --- 세션 상태(Session State) 데이터 초기화 ---
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.student_db = {
        "10101": "강백호", "10102": "서태웅", "10103": "송태섭", 
        "10104": "정대만", "10105": "채치수"
    }
    st.session_state.paid_status = {s_id: False for s_id in st.session_state.student_db}
    st.session_state.unavailable_days = {}
    st.session_state.food_opinions = []
    st.session_state.activity_opinions = []
    st.session_state.detail_opinions = []
    st.session_state.votes_food = {}
    st.session_state.votes_activity = {}
    st.session_state.votes_detail = {}

st.title("🎉 우리 반 단합대회 메이커")
st.caption("반장님을 위한 올인원 의견 취합 및 자동 투표 시스템")
st.markdown("---")

# --- 사이드바: 사용자 인증 및 회비 관리 ---
with st.sidebar:
    st.header("👤 학생 인증 및 회비 확인")
    
    st.subheader("📝 의견/투표 제출자 정보")
    user_id = st.text_input("학번 5자리 입력 (예: 10101)", key="user_id_input").strip()
    user_name = st.text_input("이름 입력 (예: 강백호)", key="user_name_input").strip()
    
    if user_id and user_name:
        if user_id not in st.session_state.student_db:
            st.session_state.student_db[user_id] = user_name
            st.session_state.paid_status[user_id] = False
        st.success(f"확인됨: {user_id} {st.session_state.student_db[user_id]}")
    else:
        st.warning("⚠️ 학번과 이름을 입력하셔야 의견 제출과 투표가 가능합니다.")

    st.markdown("---")
    st.subheader("💰 회비 납부 명부 (5번 기능)")
    st.caption("반장이 돈을 걷은 후 체크하는 칸입니다.")
    
    for s_id, s_name in sorted(st.session_state.student_db.items()):
        st.session_state.paid_status[s_id] = st.checkbox(
            f"[{s_id}] {s_name}", 
            value=st.session_state.paid_status.get(s_id, False), 
            key=f"pay_{s_id}"
        )
        
    total_students = len(st.session_state.student_db)
    paid_students = sum(st.session_state.paid_status.values())
    st.metric(label="현재 회비 납부 현황", value=f"{paid_students} / {total_students} 명", delta=f"{total_students - paid_students}명 미납")

# --- 메인 화면: 기능별 탭 분할 ---
tab1, tab2, tab3 = st.tabs(["📅 1단계: 일정 조율", "🍔 2단계: 음식/활동 투표", "🎬 3단계: 세부사항 결정"])

# --- [TAB 1] 일정 조율 (1번 기능) ---
with tab1:
    st.header("🗓️ 안되는 요일 수집 및 일정 자동 조율")
    
    days_list = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    
    with st.form("day_submission_form"):
        st.markdown("**요일 의견 제출**")
        bad_days = st.multiselect("내가 참여 불가능한 요일을 모두 고르세요:", days_list)
        submit_day = st.form_submit_button("일정 의견 제출")
        
        if submit_day:
            if not user_id or not user_name:
                st.error("❌ 사이드바에 학번과 이름을 먼저 입력해야 제출할 수 있습니다.")
            else:
                st.session_state.unavailable_days[user_id] = bad_days
                st.success(f"[{user_name}] 학생의 일정 의견이 접수되었습니다.")

    st.markdown("### 📊 실시간 일정 분석 결과")
    if st.session_state.unavailable_days:
        impossible_counts = {day: 0 for day in days_list}
        for s_id, d_list in st.session_state.unavailable_days.items():
            for d in d_list:
                impossible_counts[d] += 1
                
        possible_counts = {day: total_students - impossible_counts[day] for day in days_list}
        
        df_schedule = pd.DataFrame({
            "요일": days_list,
            "참여 가능 인원(명)": [possible_counts[d] for d in days_list],
            "불가능 인원(명)": [impossible_counts[d] for d in days_list]
        }).set_index("요일")
        
        st.dataframe(df_schedule, use_container_width=True)
        
        max_possible = max(possible_counts.values())
        best_days = [day for day, score in possible_counts.items() if score == max_possible]
        
        st.success(f"💡 **반장 통계 추천:** 현재 가장 많이 모일 수 있는 요일은 **[{', '.join(best_days)}]** 입니다! (최대 {max_possible}명 참석 가능)")
    else:
        st.info("아직 제출된 일정 데이터가 없습니다.")

# --- [TAB 2] 음식 및 활동 투표 (2, 3번 기능) ---
with tab2:
    st.header("🍔 음식 & 🎉 활동 의견 자동 취합 및 투표")
    
    with st.form("opinion_main_form"):
        st.markdown("**자유 의견 내기**")
        input_food = st.text_input("먹고 싶은 음식 아이디어 입력:").strip()
        input_act = st.text_input("하고 싶은 활동 아이디어 입력:").strip()
        submit_opinion = st.form_submit_button("의견 등록")
        
        if submit_opinion:
            if not user_id or not user_name:
                st.error("❌ 사이드바에 학번과 이름을 먼저 입력해야 제출할 수 있습니다.")
            else:
                if input_food: 
                    st.session_state.food_opinions.append(input_food)
                if input_act: 
                    st.session_state.activity_opinions.append(input_act)
                st.success("의견이 성공적으로 수집되었습니다!")
                st.rerun()

    st.markdown("---")
    st.subheader("🗳️ 실시간 자동 생성 투표 플레이스")
    
    col_food, col_act = st.columns(2)
    
    with col_food:
        st.markdown("### 🍕 음식 투표 항목 (최대 5개)")
        if st.session_state.food_opinions:
            top_foods = [item for item, _ in Counter(st.session_state.food_opinions).most_common(5)]
            st.info(f"📋 자동 후보 선정: {', '.join(top_foods)}")
            
            voted_foods = st.multiselect("음식 선택 (최대 2개):", top_foods, key="select_food_vote")
            if st.button("음식 투표 완료"):
                if not user_id or not user_name:
                    st.error("❌ 학번과 이름을 입력해 주세요.")
                elif len(voted_foods) > 2:
                    st.error("❌ 1인당 최대 2표까지만 가능합니다!")
                elif len(voted_foods) == 0:
                    st.warning("⚠️ 투표할 항목을 선택해 주세요.")
                else:
                    for f in voted_foods:
                        st.session_state.votes_food[f] = st.session_state.votes_food.get(f, 0) + 1
                    st.success("음식 투표가 반영되었습니다!")
            
            if st.session_state.votes_food:
                st.bar_chart(pd.DataFrame.from_dict(st.session_state.votes_food, orient='index', columns=['득표수']))
        else:
            st.info("학생들의 음식 의견이 모이면 투표 란이 활성화됩니다.")

    with col_act:
        st.markdown("### 🎯 대분류 활동 투표 항목 (최대 3개)")
        if st.session_state.activity_opinions:
            top_acts = [item for item, _ in Counter(st.session_state.activity_opinions).most_common(3)]
            st.info(f"📋 자동 후보 선정: {', '.join(top_acts)}")
            
            voted_acts = st.multiselect("활동 선택 (최대 2개):", top_acts, key="select_act_vote")
            if st.button("활동 투표 완료"):
                if not user_id or not user_name:
                    st.error("❌ 학번과 이름을 입력해 주세요.")
                elif len(voted_acts) > 2:
                    st.error("❌ 1인당 최대 2표까지만 가능합니다!")
                elif len(voted_acts) == 0:
                    st.warning("⚠️ 투표할 항목을 선택해 주세요.")
                else:
                    for a in voted_acts:
                        st.session_state.votes_activity[a] = st.session_state.votes_activity.get(a, 0) + 1
                    st.success("활동 투표가 반영되었습니다!")
                    st.rerun()
            
            if st.session_state.votes_activity:
                st.bar_chart(pd.DataFrame.from_dict(st.session_state.votes_activity, orient='index', columns=['득표수']))
        else:
            st.info("학생들의 활동 의견이 모이면 투표 란이 활성화됩니다.")

# --- [TAB 3] 세부 사항 결정 (4번 기능) ---
with tab3:
    st.header("🎬 3단계: 확정된 활동의 세부 사항 투표")
    
    current_winner_activity = "선정된 활동"
    if st.session_state.votes_activity:
        current_winner_activity = max(st.session_state.votes_activity, key=st.session_state.votes_activity.get)
        st.success(f"👑 현재 1위 대분류 활동: **[{current_winner_activity}]**")
    else:
        st.warning("⚠️ 2단계 대분류 활동 투표가 진행되어야 실시간 세부 연동이 가능합니다.")

    with st.form("detail_opinion_form"):
        st.markdown(f"**💡 '{current_winner_activity}'를 한다면 구체적으로 뭘 할까요?**")
        input_detail = st.text_input("아이디어 제출 (예: 영화 제목, 게임 이름 등):").strip()
        submit_detail = st.form_submit_button("세부 의견 등록")
        
        if submit_detail:
            if not user_id or not user_name:
                st.error("❌ 사이드바에 학번과 이름을 먼저 입력해야 제출할 수 있습니다.")
            elif input_detail:
                st.session_state.detail_opinions.append(input_detail)
                st.success("세부 아이디어가 반영되었습니다!")
                st.rerun()

    st.markdown("---")
    st.subheader(f"🏆 '{current_winner_activity}' 최종 세부 항목 투표 (최대 3개)")
    
    if st.session_state.detail_opinions:
        top_details = [item for item, _ in Counter(st.session_state.detail_opinions).most_common(3)]
        st.info(f"📋 자동 선정된 세부 후보군: {', '.join(top_details)}")
        
        voted_details = st.multiselect("최종 세부 안건 선택 (최대 2개):", top_details, key="select_detail_vote")
        if st.button("최종 투표 제출"):
            if not user_id or not user_name:
                st.error("❌ 학번과 이름을 입력해 주세요.")
            elif len(voted_details) > 2:
                st.error("❌ 1인당 최대 2표까지만 선택 가능합니다!")
            elif len(voted_details) == 0:
                st.warning("⚠️ 항목을 선택해 주세요.")
            else:
                for d in voted_details:
                    st.session_state.votes_detail[d] = st.session_state.votes_detail.get(d, 0) + 1
                st.success("최종 세부 투표가 반영되었습니다!")
        
        if st.session_state.votes_detail:
            st.write("📈 **최종 세부 투표 현황:**")
            st.bar_chart(pd.DataFrame.from_dict(st.session_state.votes_detail, orient='index', columns=['득표수']))
    else:
        st.info("세부 의견 의견이 제출되면 투표 시스템이 가동됩니다.")

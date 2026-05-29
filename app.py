import streamlit as st

# 제목
st.title("🌟 연예인 소개 앱")

# 연예인 데이터
celebrities = {
    "아이유": {
        "직업": "가수 / 배우",
        "대표작": "좋은 날, 호텔 델루나"
    },
    "BTS": {
        "직업": "아이돌 그룹",
        "대표작": "Dynamite"
    },
    "뉴진스": {
        "직업": "걸그룹",
        "대표작": "Hype Boy"
    }
}

# 선택창
selected = st.selectbox(
    "연예인을 선택하세요",
    list(celebrities.keys())
)

# 정보 출력
st.subheader(f"{selected} 정보")
st.write(f"직업: {celebrities[selected]['직업']}")
st.write(f"대표작: {celebrities[selected]['대표작']}")

# 이미지
st.image(
    "https://images.unsplash.com/photo-1516280440614-37939bbacd81",
    caption="Celebrity App"
)

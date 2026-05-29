# 가장 간단한 스트림릿 연예인 앱

## 1. GitHub에 올릴 파일

아래 2개 파일만 만들면 됩니다.

---

## app.py

```python
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
```

---

## requirements.txt

```txt
streamlit
```

---

# 2. 실행 방법

터미널에 아래 입력:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

# 3. Streamlit Cloud 배포 방법

1. GitHub에 파일 업로드
2. Streamlit Cloud 접속
3. GitHub 연결
4. app.py 선택
5. Deploy 클릭

---

# 4. 폴더 구조

```txt
my-app/
 ├── app.py
 └── requirements.txt
```

---

# 5. 오류 안 나게 하는 팁

* 파일 이름은 반드시 `app.py`
* requirements.txt에 `streamlit` 꼭 작성
* Python 파일 저장 후 업로드
* 들여쓰기(space) 수정하지 말기



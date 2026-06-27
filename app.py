import streamlit as st
from google import genai
from google.genai import types

# 1. 어플 기본 설정
st.set_page_config(
    page_title="냉장고를 부탁해",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 💡 여기에 배경색과 글자색을 바꾸는 스타일 코드를 추가합니다!
st.markdown("""
    <style>
    /* 🌐 구글 폰트 적용 */
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

    /* 💡 화면 전체(가장 바깥쪽 껍데기)를 세로 정렬이 가능한 구조로 변경 */
    .stAppViewContainer {
        display: flex;
        align-items: center;      /* 세로 기준 정중앙 정렬 */
        justify-content: center;   /* 가로 기준 정중앙 정렬 */
        height: 100vh;            /* 화면 높이를 꽉 채우기 */
    }

    /* 진짜 내용물이 들어있는 상자 스타일 */
    .stApp {
        background-color: #1E3F20;
        font-family: 'Gowun Dodum', sans-serif !important;
        text-align: center;
        width: 100%;
        max-width: 500px;         /* 폰에서 너무 퍼지지 않게 크기 제한 */
        margin: auto;             /* 자동 여백 채우기 */
    }
    
    /* 1. "냉장고를 부탁해" 타이틀 크기 및 정렬 */
    .stApp h1 {
        font-size: 28px !important;
        text-align: center !important;
        margin-bottom: 20px;
    }
    
    /* 모든 일반 글자 스타일 및 가운데 정렬 */
    .stApp p, .stApp h2, .stApp h3, .stApp span {
        color: #FFFFFF !important;
        font-family: 'Gowun Dodum', sans-serif !important;
        text-align: center !important;
    }
    
    /* 입력창 위의 안내 글씨 정렬 */
    .stApp label {
        color: #FFFFFF !important;
        font-family: 'Gowun Dodum', sans-serif !important;
        display: block;
        text-align: center !important;
    }
    
/* 🛠️ 입력창 글자색 흰색으로, 배경도 약간 어둡게 수정 */
    .stTextInput input {
        background-color: #153017 !important; /* 입력창 배경색 */
        color: #FFFFFF !important;            /* 💡 글자색을 흰색으로! */
        font-family: 'Gowun Dodum', sans-serif !important;
        text-align: center !important;
        border: 1px solid #4CAF50 !important;
    }

    /* 버튼 스타일 및 중앙 배치 */
    div.stButton {
        text-align: center !important;
    }
    div.stButton > button:first-child {
        background-color: #2E7D32;
        color: white !important;
        border: 1px solid #4CAF50;
        border-radius: 10px;
        font-weight: bold;
        font-family: 'Gowun Dodum', sans-serif !important;
        padding: 10px 20px;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #388E3C;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# [필수] 구글 제미나이 통행증(API Key) 설정
# 아래 따옴표 안에 발급받으신 API Key를 꼭 다시 넣어주세요!
GEMINI_API_KEY = "AQ.Ab8RN6IzRT_BMlo367SUF56K1JpncpDTI_NBSTlOAIlXg0jPvw"

# 제미나이 클라이언트 프로그램 초기화
@st.cache_resource
def get_ai_client():
    return genai.Client(api_key=GEMINI_API_KEY)

client = get_ai_client()

# 예쁜 카드 레이아웃 스타일 설정 (CSS)
st.markdown("""
    <style>
    .recipe-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 6px solid #4CAF50;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .badge-container {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
    }
    .badge-time {
        background-color: #E8F5E9;
        color: #2E7D32;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    .badge-level {
        background-color: #FFF3E0;
        color: #E65100;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# [수정 완료] 깔끔하게 다듬은 어플 타이틀과 안내 문구
st.title("🍳 냉장고를 부탁해!")
st.write("가진 재료를 입력하시면 레시피를 생성해 드려요.")

# 2. 식재료 입력받기
ingredients = st.text_input("식재료를 쉼표(,)로 구분해서 입력하세요 (예: 스팸, 계란, 파)")

# 어플이 기억해야 할 상태 설정 (추천받은 메뉴 기록들)
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. 식재료를 입력했을 때 작동
if ingredients:
    # '다른 메뉴 보기' 버튼을 누르거나 처음 입력했을 때 AI에게 요청
    if st.button("맘에 안 들어요, 다른 메뉴 볼래요!", use_container_width=True) or not st.session_state.history:
        
        with st.spinner("냉장고 재료로 새로운 레시피를 고민하고 있습니다... 🧠"):
            # 기존에 추천했던 메뉴들과 겹치지 않게 하기 위한 프롬프트 작성
            past_menus = ", ".join(st.session_state.history) if st.session_state.history else "없음"
            
            prompt = f"""
            사용자의 냉장고 재료: {ingredients}
            이전 추천 메뉴 목록: {past_menus}
            
            위 재료를 활용해서 만들 수 있는 맛있는 요리를 딱 1개만 추천해줘. 
            단, 이전 추천 메뉴 목록에 있는 요리와는 무조건 다른 새로운 요리여야 해.
            반드시 아래의 JSON 형식을 정확히 지켜서 한국어로 답변해줘. 다른 설명은 하지마.

            {{
                "menu": "요리 이름 (이쁜 이모지 포함)",
                "time": "조리 시간 (예: 20분)",
                "level": "난이도 (예: ⚡ 쉬움, ⭐ 보통, 🔥 어려움)",
                "ingredients": ["재료1 정확한 양", "재료2 정확한 양"],
                "steps": ["1단계 설명", "2단계 설명"]
            }}
            """
            
            try:
                # Gemini 2.5 Flash 모델에게 요청
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                
                # AI가 준 정답을 파이썬 데이터로 변환해서 저장
                import json
                recipe_data = json.loads(response.text)
                st.session_state.current_recipe = recipe_data
                st.session_state.history.append(recipe_data['menu'])
                
            except Exception as e:
                st.error("AI와 연결 중 오류가 발생했습니다. API Key를 확인해 주세요.")
                st.stop()

    # 현재 생성된 레시피 화면에 그리기
    if 'current_recipe' in st.session_state:
        current = st.session_state.current_recipe
        
        # 예쁜 카드 레이아웃
        st.markdown(f"""
            <div class="recipe-card">
                <h2 style="margin-top:0; color:#1E293B;">{current['menu']}</h2>
                <div class="badge-container">
                    <span class="badge-time">⏰ 조리시간: {current['time']}</span>
                    <span class="badge-level">📊 난이도: {current['level']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📌 필수 재료")
            for ing in current['ingredients']:
                st.write(f"• {ing}")
                
        with col2:
            st.subheader("🍳 조리 순서")
            for i, step in enumerate(current['steps'], 1):
                st.write(f"**{i}.** {step}")

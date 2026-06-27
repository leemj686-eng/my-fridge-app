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

# 🎨 화면 테마, 폰트, 정렬 및 테두리 선(Border) 추가 스타일 설정
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

.stAppViewContainer {
    display: flex;
    justify-content: center;
    background-color: #112512; /* 외곽 테두리 바깥쪽은 조금 더 어두운 배경으로 처리 */
}

.stApp {
    background-color: #1E3F20;
    font-family: 'Gowun Dodum', sans-serif !important;
    text-align: center;
    width: 100%;
    max-width: 500px;
    margin: auto;
    
    /* 🛠️ [추가] 최외곽 안쪽에 하얀색 얇은 테두리선 넣기 */
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.stApp h1 {
    font-size: 28px !important;
    text-align: center !important;
    margin-bottom: 20px;
}

.stApp p, .stApp h2, .stApp h3, .stApp span, .stApp label {
    color: #FFFFFF !important;
    font-family: 'Gowun Dodum', sans-serif !important;
    text-align: center !important;
}

/* 🛠️ [추가] 가로로 정렬된 글씨와 입력창의 높이를 완벽하게 한 줄로 맞추는 마법 */
.row-container {
    display: table !important;
    width: 100% !important;
    margin-top: 15px !important;
    margin-bottom: 15px !important;
}
.label-box {
    display: table-cell !important;
    vertical-align: middle !important;
    width: 25% !important;
    text-align: right !important;
    padding-right: 12px !important;
    color: #FFFFFF !important;
    font-size: 16px !important;
}
.input-box {
    display: table-cell !important;
    vertical-align: middle !important;
    width: 75% !important;
}

.stTextInput input {
    background-color: #153017 !important;
    color: #FFFFFF !important;
    font-family: 'Gowun Dodum', sans-serif !important;
    text-align: center !important;
    border: 1px solid #4CAF50 !important;
}

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

/* 메인 화면 글자 상자들의 얼룩덜룩한 배경 투명하게 제거 */
div[data-testid="stMarkdownContainer"] {
    background-color: transparent !important;
    box-shadow: none !important;
    padding: 0px !important;
}

/* AI 레시피 결과가 들어갈 카드 레이아웃 */
.recipe-card {
    background-color: #153017 !important;
    padding: 25px !important;
    border-radius: 15px !important;
    border-left: 6px solid #4CAF50 !important;
    margin-top: 20px !important;
    margin-bottom: 20px !important;
}

.recipe-card h2 {
    color: #FFFFFF !important;
}

.badge-container {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    justify-content: center;
}

.badge-time {
    background-color: #2E7D32 !important;
    color: #FFFFFF !important;
    padding: 5px 12px !important;
    border-radius: 20px !important;
    font-weight: bold !important;
    font-size: 14px !important;
}

.badge-level {
    background-color: #E65100 !important;
    color: #FFFFFF !important;
    padding: 5px 12px !important;
    border-radius: 20px !important;
    font-weight: bold !important;
    font-size: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# [필수] 구글 제미나이 통행증(API Key) 설정
GEMINI_API_KEY = "AQ.Ab8RN6IzRT_BMlo367SUF56K1JpncpDTI_NBSTlOAIlXg0jPvw"

# 제미나이 클라이언트 프로그램 초기화
@st.cache_resource
def get_ai_client():
    return genai.Client(api_key=GEMINI_API_KEY)

client = get_ai_client()

# 화면 상단 여백 확보
st.write("")
st.write("")

# 타이틀 및 첫 번째 안내 문구 (줄바꿈 반영)
st.title("🍳 냉장고를 부탁해!")
st.markdown("가진 재료를 입력하시면 <br>맘에 들 때까지 레시피를 생성해 드려요.", unsafe_allow_html=True)

# 두 번째 안내 문구
st.markdown("식재료를 쉼표(,)로 구분해서 입력하세요 <br>(예: 스팸, 계란, 파)", unsafe_allow_html=True)

# 🛠️ [수정 완료] HTML 마법을 결합하여 '식재료 :'와 입력칸을 완벽히 정중앙 한 줄로 배치!
st.markdown('<div class="row-container">', unsafe_allow_html=True)
col_label, col_input = st.columns([1, 3])

with col_label:
    st.markdown("<div class='label-box'><b>식재료 :</b></div>", unsafe_allow_html=True)

with col_input:
    ingredients = st.text_input("", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# 어플이 기억해야 할 상태 설정 (추천받은 메뉴 기록들)
if 'history' not in st.session_state:
    st.session_state.history = []

# 3. 식재료를 입력했을 때 작동
if ingredients:
    if st.button("맘에 안 들어요, 다른 메뉴 볼래요!", use_container_width=True) or not st.session_state.history:
        
        with st.spinner("냉장고 재료로 새로운 레시피를 고민하고 있습니다... 🧠"):
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
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                
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
        
        st.markdown(f"""
            <div class="recipe-card">
                <h2 style="margin-top:0; text-align:center;">{current['menu']}</h2>
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

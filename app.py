import streamlit as st

st.title("API Key 테스트 화면")

try:
    # 스트림릿 시크릿에서 키를 잘 가져오는지 확인
    api_key = st.secrets["GEMINI_API_KEY"]
    st.success(f"시크릿 키를 성공적으로 불러왔습니다! 키의 첫 5자리: {api_key[:5]}")
except Exception as e:
    st.error("🚨 여전히 시크릿 키를 찾을 수 없습니다. (NameError 발생)")
    st.write("아래 Secrets 설정 방법을 다시 확인해주세요.")

import streamlit as st
from caltest import festival_calendar

# options = ['달력', '지도']
# # option = st.sidebar.selectbox('축제', options)
# option = st.radio('축제', options)

# if option == '달력':

festival_calendar()

st.markdown("""
<style>
/* selectbox 드롭다운 메뉴 스타일 */
div[data-baseweb="select"] > div {
    background-color: #444444 !important;  /* 드롭다운 배경 */
    color: #ffc60b !important;             /* 선택된 항목 글자색 */
    border-radius: 5px;
    padding: 5px;
    min-height: 55px !important;  /* 전체 셀렉트박스 높이 */
    padding-top: 10px !important;  /* 내부 여백 조절 */
    padding-bottom: 10px !important;
}

/* 드롭다운 항목 리스트 */
ul[role="listbox"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

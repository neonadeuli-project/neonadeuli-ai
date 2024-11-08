from openai import OpenAI
from collections import deque
import streamlit as st
from utils.prompts import QUIZ_PROMPT
from utils.info import INFO
from utils.text_split import quiz

st.set_page_config(page_title="너나들이", page_icon="https://avatars.githubusercontent.com/u/179866435?s=48&v=5")

@st.dialog(title=" ", width="large")
def info():
    st.markdown(INFO, unsafe_allow_html=True)

@st.dialog(title="정답입니다!", width="large")
def quiz_explane():
    st.markdown(st.session_state['quiz']['explane'], unsafe_allow_html=True)    

with st.sidebar:
    password = st.text_input("Password", key="chatbot_api_key", type="password")
    st.divider()
    if st.button("안내사항", icon="⚠️"): info()
    st.link_button(label="너나들이", url="https://www.notion.so/9bfd00945c0f41c285fd165f4810ff75?pvs=4", help="너나들이 QA페이지", icon="🚨")

st.title("퀴즈 챗봇")
st.session_state['system_prompt'] = [{"role":"system", "content":QUIZ_PROMPT}]

if "messages" not in st.session_state:
    st.session_state["messages"] = deque([])

if not password or password != st.secrets["Password"]:
    st.info("Password를 확인해주세요.")
    st.stop()

def make_quiz():
    client = OpenAI(api_key=st.secrets['OpenAI_Key'])
    st.session_state.messages.append({"role": "user", "content": f"{type}에 대한 퀴즈를 출제해줘."})

    # message 수 9개 이하로 조정 
    while len(st.session_state.messages) >= 9:
        st.write(st.session_state.messages)
        st.session_state.messages.popleft()

    # st.chat_message("user").write(input)
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=st.session_state.system_prompt+list(st.session_state.messages)
    )
    msg = response.choices[0].message.content
    quiz_dict = quiz(msg)
    st.session_state['quiz'] = quiz_dict
    st.session_state.messages.append({"role": "assistant", "content": msg})

def answer_check(my_answer:str):
    if my_answer == st.session_state['quiz']['answer']:
        quiz_explane()
        st.session_state['messages'] = deque([])
        st.session_state['quiz'] = {}


st.divider()
left, right = st.columns(2)
with left:
    type = st.selectbox(
        "국가 유산을 선택하세요",
        options=("경복궁", "불국사")
    )
with right:
    pp = st.button("퀴즈출제", on_click=make_quiz)
    print(pp)
st.divider()

# 버튼 구성
if len(st.session_state.messages) > 0:
    st.chat_message("assistant").write(st.session_state.messages[-1]['content'])
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("1번"):
            answer_check("1번")
    with col2:
        if st.button("2번"):
            answer_check("2번")
    with col3:
        if st.button("3번"):
            answer_check("3번")
    with col4:
        if st.button("4번"):
            answer_check("4번")
    with col5:
        if st.button("5번"):
            answer_check("5번")
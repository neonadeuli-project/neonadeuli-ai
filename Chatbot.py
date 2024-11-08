from openai import OpenAI
from collections import deque
import streamlit as st
from utils.prompts import CHAT_PROMPT, SUMMARY_PROMPT, COMMENTATOR_PROMPT
from utils.info import INFO
from utils.text_split import quiz, summary
from datetime import datetime
import time

# 파비콘
st.set_page_config(page_title="너나들이", page_icon="https://avatars.githubusercontent.com/u/179866435?s=48&v=5")

# 안내사항
@st.dialog(title=" ", width="large")
def info():
    st.markdown(INFO, unsafe_allow_html=True)

# 대화 요약 버튼
@st.dialog(title=" ", width="large")
def summarize():
    client = OpenAI(api_key=st.secrets['OpenAI_Key'])
    with st.spinner("대화를 요약중입니다."):
        time.sleep(2)
        summarized_content = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role":"assistant", "content":SUMMARY_PROMPT}]+list(st.session_state.messages)
        )
    st.markdown(summary(["2024-07-10", datetime.today().strftime("%Y-%m-%d"), summarized_content.choices[0].message.content]), unsafe_allow_html=True)

# 사이드바 구성
with st.sidebar:
    password = st.text_input("Password", key="chatbot_api_key", type="password")
    st.divider()
    chatbot_type = st.radio(
        "챗봇의 유형을 선택하세요",
        ["국가유산챗봇", "국가유산해설사"],
        captions=["국가유산과 채팅을 주고받습니다.", "국가유산해설사와 같은 역할을 수행합니다."]
    )
    if "chatbot_type" in st.session_state and chatbot_type != st.session_state['chatbot_type']:
        st.session_state["messages"] = deque([])
    st.session_state['chatbot_type'] = chatbot_type
    st.divider()
    if chatbot_type == "국가유산해설사":
        option = st.selectbox(
            label="국가유산을 선택하세요",
            options=("경복궁", "불국사")
        )
        st.divider()
    st.session_state['system_prompt'] = [{"role":"system","content":CHAT_PROMPT}] if chatbot_type == "국가유산챗봇" else [{"role":"system","content":COMMENTATOR_PROMPT(option)}]
    if st.button("안내사항", icon="⚠️"): info()
    st.link_button(label="너나들이", url="https://www.notion.so/9bfd00945c0f41c285fd165f4810ff75?pvs=4", help="너나들이 QA페이지", icon="🚨")
    if "messages" in st.session_state and len(st.session_state.messages) >= 2:
        if st.button("대화요약", icon="📝"): summarize()

# 중앙 타이틀
st.title(f"{chatbot_type}" if chatbot_type == "국가유산챗봇" else f"{chatbot_type} - {option}")


if "messages" not in st.session_state:
    st.session_state["messages"] = deque([])

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if input := st.chat_input():
    if not password or password != st.secrets["Password"]:
        st.info("Password를 확인해주세요.")
        st.stop()
    client = OpenAI(api_key=st.secrets['OpenAI_Key'])
    st.session_state.messages.append({"role": "user", "content": input})
    
    # message 수 9개 이하로 조정 
    while len(st.session_state.messages) >= 9:
        st.write(st.session_state.messages)
        st.session_state.messages.popleft()

    st.chat_message("user").write(input)
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=st.session_state.system_prompt+list(st.session_state.messages)
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
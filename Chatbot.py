from openai import OpenAI
from collections import deque
import streamlit as st
from utils.prompts import CHAT_PROMPT, QUIZ_PROMPT, SUMMARY_PROMPT
from utils.info import INFO
from utils.text_split import quiz, summary
from datetime import datetime

st.set_page_config(page_title="너나들이", page_icon="https://avatars.githubusercontent.com/u/179866435?s=48&v=5")

@st.dialog(title=" ", width="large")
def info():
    st.markdown(INFO, unsafe_allow_html=True)

@st.dialog(title=" ", width="large")
def summarize():
    client = OpenAI(api_key=st.secrets['OpenAI_Key'])
    summarized_content = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[{"role":"assistant", "content":SUMMARY_PROMPT}]+list(st.session_state.messages)
    )
    print(summarized_content.choices[0].message.content.split('\n'))
    st.markdown(summary(["2024-07-10", datetime.today().strftime("%Y-%m-%d"), summarized_content.choices[0].message.content]), unsafe_allow_html=True)

with st.sidebar:
    password = st.text_input("Password", key="chatbot_api_key", type="password")
    st.divider()
    type = st.radio("챗봇 유형을 선택해주세요.",["Chatbot", "Quiz"], captions=["국가 유산에 관해 대화하는 챗봇", "국가 유산에 관한 퀴즈를 출제하는 챗봇"])
    if type == 'Chatbot':
        st.session_state['system_prompt'] = [{"role":"assistant", "content":CHAT_PROMPT}]
    elif type == 'Quiz':
        st.session_state['system_prompt'] = [{"role":"assistant", "content":QUIZ_PROMPT}]
    st.divider()
    if st.button("안내사항", icon="⚠️"): info()
    if st.button("대화요약", icon="📝"): summarize()
    st.link_button(label="너나들이", url="https://www.notion.so/9bfd00945c0f41c285fd165f4810ff75?pvs=4", help="너나들이 QA페이지", icon="🚨")

st.title(f"{type}")



if "messages" not in st.session_state:
    st.session_state["messages"] = deque([])

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


if input := st.chat_input():
    if not password or password != st.secrets["Password"]:
        st.info("Password를 확인해주세요.")
        st.stop()
    client = OpenAI(api_key=st.secrets['OpenAI_Key'])
    # if type == "Image":
    #     st.session_state.messages.append({"role": "user", "content": [{"type":"text", "text":prompt}, {"type":"image_url", "image_url": {"url": f"data:image/png;base64,{encoded_img}"}}]})
    st.session_state.messages.append({"role": "user", "content": input})
    
    # message 수 9개 이하로 조정 
    while len(st.session_state.messages) >= 9:
        st.write(st.session_state.messages)
        st.session_state.messages.popleft()

    st.chat_message("user").write(input)
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=st.session_state.system_prompt+list(st.session_state.messages)
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
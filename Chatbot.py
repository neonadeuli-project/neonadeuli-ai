from openai import OpenAI
from collections import deque
import streamlit as st
import base64
from utils.prompts import CHAT_PROMPT, QUIZ_PROMPT

st.set_page_config(page_title="너나들이", page_icon="https://avatars.githubusercontent.com/u/179866435?s=48&v=5")

with st.sidebar:
    password = st.text_input("Password", key="chatbot_api_key", type="password")
    st.divider()
    type = st.radio("챗봇 유형을 선택해주세요.",["Chatbot", "Quiz"], captions=["국가 유산에 관해 대화하는 챗봇", "국가 유산에 관한 퀴즈를 출제하는 챗봇"])
    if type == 'Chatbot':
        st.session_state['system_prompt'] = [{"role":"assistant", "content":CHAT_PROMPT}]
    elif type == 'Quiz':
        st.session_state['system_prompt'] = [{"role":"assistant", "content":QUIZ_PROMPT}]
    st.divider()
    "[![QA 제보](https://avatars.githubusercontent.com/u/179866435?s=48&v=)](https://www.notion.so/9bfd00945c0f41c285fd165f4810ff75?pvs=4 'QA 페이지')"

st.title(f"{type}")



if "messages" not in st.session_state:
    st.session_state["messages"] = deque([])

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not password or password != st.secrets["Password"]:
        st.info("Password를 확인해주세요.")
        st.stop()
    client = OpenAI(api_key=st.secrets['OpenAI_Key'])
    # if type == "Image":
    #     st.session_state.messages.append({"role": "user", "content": [{"type":"text", "text":prompt}, {"type":"image_url", "image_url": {"url": f"data:image/png;base64,{encoded_img}"}}]})
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # message 수 9개 이하로 조정 
    while len(st.session_state.messages) >= 9:
        st.write(st.session_state.messages)
        st.session_state.messages.popleft()

    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=st.session_state.system_prompt+list(st.session_state.messages)
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
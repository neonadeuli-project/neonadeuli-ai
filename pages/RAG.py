from openai import OpenAI
from collections import deque
import streamlit as st
from utils.prompts import CHAT_PROMPT, SUMMARY_PROMPT, COMMENTATOR_PROMPT
from utils.info import INFO
from utils.text_split import summary
from datetime import datetime
import time

# 파비콘
st.set_page_config(page_title="너나들이", page_icon="https://avatars.githubusercontent.com/u/179866435?s=48&v=5")

# 안내사항
@st.dialog(title=" ", width="large")
def info():
    st.markdown(INFO, unsafe_allow_html=True)

# 대화 요약 버튼
# @st.dialog(title=" ", width="large")
# def summarize():
#     client = OpenAI(api_key=st.secrets['OpenAI_Key'])
#     with st.spinner("대화를 요약중입니다."):
#         time.sleep(2)
#         summarized_content = client.chat.completions.create(
#             model="gpt-4o-mini", 
#             messages=[{"role":"assistant", "content":SUMMARY_PROMPT}]+list(st.session_state.messages)
#         )
#     st.markdown(summary(["2024-07-10", datetime.today().strftime("%Y-%m-%d"), summarized_content.choices[0].message.content]), unsafe_allow_html=True)

# 사이드바 구성
with st.sidebar:
    password = st.text_input("Password", key="chatbot_api_key", type="password")
    st.divider()
    if st.button("안내사항", icon="⚠️"): info()
    st.link_button(label="너나들이", url="https://www.notion.so/9bfd00945c0f41c285fd165f4810ff75?pvs=4", help="너나들이 QA페이지", icon="🚨")

# 중앙 타이틀
st.title("RAG 실험실")


if "client" in st.session_state:
    m = st.session_state['client'].beta.threads.messages.list(thread_id=st.session_state["thread_id"])
    for dd in m.data[::-1]:
        st.chat_message(dd.role).write(dd.content[0].text.value)

if input := st.chat_input():
    if not password or password != st.secrets["Password"]:
        st.info("Password를 확인해주세요.")
        st.stop()
    if 'client' not in st.session_state:
        client = OpenAI(api_key=st.secrets['OpenAI_Key'])
        st.session_state['client'] = client
    else:
        client = st.session_state['client']

    # 어시스트, 스레드 생성
    if "thread_id" not in st.session_state:
        rag = client.beta.assistants.create(
        name="문화해설사",
        instructions="너는 대한민국 국가유산 문화해설사야. 파일 속 내용을 참고해 답변해줘. 파일에 내용이 없다면 원래 알고 있는 지식을 바탕으로 답해줘. 파일에 대한 언급 없이 답해줘.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [st.secrets['VECTOR_DB_ID']]}}
        )
        rag_thread = client.beta.threads.create()
        st.session_state["thread_id"] = rag_thread.id
        st.session_state["assistant_id"] = rag.id

    # st.session_state.messages.append({"role": "user", "content": input})
    message = client.beta.threads.messages.create(
        thread_id=st.session_state["thread_id"],
        role="user",
        content=input
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state["thread_id"],
        assistant_id=st.session_state["assistant_id"]
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state["thread_id"]
        )
    message_content = list(messages)[0].content[0].text
    annotations = message_content.annotations
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, "")

    st.chat_message("user").write(input)
    msg = message_content.value
    st.chat_message("assistant").write(msg)
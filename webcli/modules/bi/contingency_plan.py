import streamlit as st
from vertexai.generative_models import ChatSession
from typing import Generator

from vega_datasets import data


left, right = st.columns([0.6, 0.4], border=True, vertical_alignment="top")

data = [
    (data.barley(), dict(x="variety", y="yield", color="site", horizontal=True)),
    (data.barley(), dict(x="year", y="yield", color="site", stack=False)),
]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Streamed response emulator
def get_response(chat: ChatSession, prompt: str) -> Generator[str]:
    responses = chat.send_message(prompt, stream=True)
    for chunk in responses:
        yield chunk.text


@st.dialog("Change BI figure")
def change_fig(tab: int, col: int):
    f"change fig on {tab} {col}"


with right:
    st.subheader(":material/support_agent: Planning Companion", divider="grey")
    chat_history = st.container(border=True, height=650)
    with chat_history:
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    with st.container(border=False):
        # Accept user input
        if prompt := st.chat_input("What is up?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with chat_history:
                with st.chat_message("user"):
                    st.markdown(prompt)

            # Display assistant response in chat message container
            with chat_history:
                with st.chat_message("assistant"):
                    response = st.write_stream(
                        get_response(st.session_state.aisession, prompt)
                    )
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})


with left:
    st.subheader(":material/checklist: _Action List_", divider="red")
    with st.container(border=True, height=150):
        st.markdown(
            """
         - [ ] Supplier 102の供給への影響を早急に確認してください。
         - 供給不可の場合、下記順序で対応してください
           - [ ] Supplier 103の追加供給の可能性確認
           - [ ] Supplier 101の追加供給の可能性確認
         """
        )

    st.subheader(":material/monitoring: _BI PickUps_", divider="blue")
    tabs = st.tabs(["1. XXX", "2. XXX", "3. XXX", ":material/settings: configure"])
    for tab_idx, tab in enumerate(tabs[:-1]):
        with tab:
            with st.container():
                for col_idx, col in enumerate(st.columns(2)):
                    with col:
                        with st.container(height=400, border=True):
                            val, kwarg = data[col_idx % 2]
                            st.bar_chart(val, **kwarg)
    with tabs[-1]:
        if st.button(
            "change figures",
            icon=":material/settings:",
            type="tertiary",
        ):
            change_fig(tab_idx, col_idx)

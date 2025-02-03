import streamlit as st
from typing import Any
import pandas as pd
from io import StringIO

from vega_datasets import data


left, right = st.columns([0.6, 0.4], border=True, vertical_alignment="top")

data = [
    (data.barley(), dict(x="variety", y="yield", color="site", horizontal=True)),
    (data.barley(), dict(x="year", y="yield", color="site", stack=False)),
]


@st.dialog("Change BI figure")
def change_fig(tab: int, col: int):
    f"change fig on {tab} {col}"


def run_action(infos: list[dict[str, Any]]):
    for info in infos:
        print(f"got {info}")
        if info["type"] == "plot":
            input = info["input"]
            if input["plot_type"] == "line":
                st.line_chart(
                    data=pd.read_json(StringIO(input["source"])),
                    x=input["x_axis"],
                    y=input["y_axis"],
                )
            elif input["plot_type"] == "bar":
                st.bar_chart(
                    data=pd.read_json(StringIO(input["source"])),
                    x=input["x_axis"],
                    y=input["y_axis"],
                )
            else:
                return None


with right:
    st.subheader(":material/support_agent: Planning Companion", divider="grey")
    chat_history = st.container(border=True, height=650)
    with chat_history:
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                message["content"]
                if "fig" in message and message["fig"] is not None:
                    message["fig"]

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
                    resp = st.session_state.aiagent.send_message(
                        prompt,
                        st.session_state.strategy_scenario,
                        st.session_state.agent_ai_last_msg,
                    )
                    response = st.write(resp["msg"])
                    st.session_state.agent_ai_last_msg = response
                    st.session_state.strategy_scenario = resp["strategy"]
                    fig = run_action(resp["actions"])

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.messages.append(
                {"role": "assistant", "content": response, "fig": fig}
            )


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

import streamlit as st

from modules.top.contingency_plan.reporter import render_report
from modules.top.contingency_plan.companion import render_agent_interface
from modules.top.contingency_plan.calculator import provision_data


@st.dialog("セッションを開始しますか?")
def start_session():
    c1, c2 = st.columns(2)
    with c1:
        if st.button("はい"):
            provision_data("V001")
    with c2:
        if st.button("いいえ"):
            st.info("待機します, ×ボタンから抜けてください")


# UI
if st.session_state.event is None:
    st.info("重要なイベントはありません")
    st.stop()

if st.session_state.agent["status"] == "deactive":
    "# イベント対応"
    st.warning("**イベントを検知しました, 開始ボタンから状況を開始してください**")
    if st.button("状況を開始"):
        start_session()
    st.stop()


left, right = st.columns([0.6, 0.4], vertical_alignment="top")

with right:
    with st.container(border=True, height=800):
        chat_history = st.session_state.agent["chat_history"]
        render_agent_interface(chat_history)

with left:
    with st.container(border=True, height=800):
        jinja_env = st.session_state.jinja
        strategy_scenario = st.session_state.agent["model"].strategy
        event_scenario = st.session_state.event
        datahub = st.session_state.datahub
        render_report(jinja_env, event_scenario, strategy_scenario, datahub)

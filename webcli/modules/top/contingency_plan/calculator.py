import streamlit as st
from modules.top.contingency_plan.companion import Message


def provision_data():
    with st.status("情報取得中"):
        st.write("被害予測取得中")

        st.write("対策シナリオセッション準備中")
        prompt = f"""
        [イベントシナリオ]: {st.session_state.agent["event"]}
        eventの影響
        1. sales: {st.session_state["diff_sales_forecast"]}
        2. resource: {st.session_state["diff_resource_forecast"]}
        3. routing: {st.session_state["diff_routing_forecast"]}
        ユーザーのinput: イベントが発生しました, 3行程度で概要を説明してください.
        また今は何をしたらいいでしょうか?
        """
        response = st.session_state.agent["model"].send_message(prompt)
        st.session_state.agent["chat_history"].append(
            Message(
                actor="assistant",
                message=response.message,
                attachments=response.actions,
            )
        )
        st.session_state.agent["status"] = "active"
        st.write("完了")
        st.rerun()

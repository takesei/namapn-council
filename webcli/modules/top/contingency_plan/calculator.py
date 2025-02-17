import streamlit as st
from modules.top.contingency_plan.companion import Message


def provision_data(current_version_code: str):
    with st.status("情報取得中"):
        st.write("被害予測取得中")

        st.write("対策シナリオセッション準備中")
        event = st.session_state.event
        dhub = st.session_state.datahub
        target_version = [c.version for c in event.event_cases]

        event_effect = {tv: {} for tv in target_version}
        for name, dcont in dhub.items():
            for tv in target_version:
                try:
                    df_diff = dcont.diff([current_version_code, tv])
                    event_effect[tv][name] = df_diff
                except Exception as e:
                    print(e)

        prompt = ""
        for k, v in event_effect.items():
            prompt += f"-- {k}\n"
            for table, diff in v.items():
                prompt += f"---- {table}\n  {diff.to_json()}\n"

        prompt = f"""
        [イベントシナリオ]: {st.session_state.event}
        eventの影響
        {prompt}
        ユーザーのinput: イベントが発生しました, 3行程度で概要を説明してください.
        また今は何をしたらいいでしょうか?
        """
        response = st.session_state.agent["model"].send_message(prompt)
        st.session_state.agent["chat_history"].append(
            Message(
                actor="assistant",
                message=response.message,
                attachments=response.attachments,
            )
        )
        st.session_state.agent["status"] = "active"
        st.write("完了")
        st.rerun()

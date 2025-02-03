import streamlit as st
from libs.actions import run_action


@st.dialog("セッションを開始しますか?")
def start_session():
    c1, c2 = st.columns(2)
    res = None
    with c1:
        if st.button("はい"):
            res = True
    with c2:
        if st.button("いいえ"):
            res = False

    if res is None:
        pass
    elif res:
        with st.status("情報取得中"):
            st.write("被害予測取得中")
            impact = st.session_state.db.get("impact")
            st.write("対策シナリオセッション準備中")
            prompt = f"""
            イベントの詳細: {st.session_state.agent["event"]}
            イベントの被害: {impact}
            ユーザーのinput: イベントが発生しました, 次に何をしたらいいか教えてください
            """
            response = st.session_state.agent["model"].send_message(prompt)
            st.write("情報登録中")
            st.session_state.agent["chat_history"].append(
                {"role": "assistant", "content": response.message, "fig": None}
            )
            st.write("完了")
            st.session_state.agent["status"] = "active"
            st.rerun()
    else:
        st.info("待機します, ×ボタンから抜けてください")


if st.session_state.agent["event"] is None:
    st.info("重要なイベントはありません")
    st.stop()
if st.session_state.agent["status"] == "deactive":
    "# イベント対応"
    st.warning("**イベントを検知しました, 開始ボタンから状況を開始してください**")
    if st.button("状況を開始"):
        start_session()
    st.stop()


left, right = st.columns([0.6, 0.4], border=True, vertical_alignment="top")
with right:
    st.subheader(":material/support_agent: Planning Companion", divider="grey")
    chat_history = st.container(border=True, height=650)
    with chat_history:
        for message in st.session_state.agent["chat_history"]:
            with st.chat_message(message["role"]):
                message["content"]
                if "fig" in message and message["fig"] is not None:
                    message["fig"]

    with st.container(border=False):
        if prompt := st.chat_input("What is up?"):
            st.session_state.agent["chat_history"].append(
                {"role": "user", "content": prompt, "fig": None}
            )
            with chat_history:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    resp = st.session_state.agent["model"].send_message(prompt)
                    st.write(resp.message)
                    fig = run_action(resp.actions)
            st.session_state.agent["chat_history"].append(
                {"role": "assistant", "content": resp.message, "fig": fig}
            )


with left:
    tabs = st.tabs(["1. イベント概要", "イベント詳細", "2. 対策1", "3. 対策2"])
    with tabs[0]:
        with st.container(height=700):
            template = st.session_state.jinja.get_template("event.md")
            rdr = template.render(st.session_state.agent["event"])
            st.markdown(rdr)
    with tabs[1]:
        with st.container(height=700):
            template = st.session_state.jinja.get_template("event.md")
            rdr = template.render(st.session_state.agent["event"])
            st.markdown(rdr)
    with tabs[2]:
        with st.container(height=700):
            template = st.session_state.jinja.get_template("strategy.md")
            rdr = template.render(st.session_state.agent["model"].strategy)
            st.markdown(rdr)

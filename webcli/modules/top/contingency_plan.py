import streamlit as st
import re
from libs.actions import run_action
import pandas as pd

with st.spinner("Initialize"):
    forecasts = dict(
        sales_forecast=st.session_state.db.get("sales_forecasts"),
        resource_forecast=st.session_state.db.get("resource_forecasts"),
        routing_forecast=st.session_state.db.get("routing_forecasts"),
    )


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
            for cat, fcst in forecasts.items():
                if f"diff_{cat}" not in st.session_state:
                    col = [
                        c
                        for c in fcst.columns
                        if c
                        not in [
                            "version",
                            "quantity",
                            "cost",
                            "unit_cost",
                        ]
                    ]
                    ax = [c for c in fcst.columns if c not in ["version", *col]]
                    diff = (
                        fcst[fcst.version == "V001"]
                        .rename(columns={a: f"{a}_original" for a in ax})
                        .drop(columns=["version"])
                    )
                    evt = fcst[
                        fcst.version.isin(
                            [
                                v
                                for v in fcst.version.unique()
                                if v not in ["V001", "V002"]
                            ]
                        )
                    ]
                    for version in evt.version.unique():
                        diff = pd.merge(
                            diff,
                            evt[evt.version == version]
                            .rename(columns={a: f"{a}_{version}" for a in ax})
                            .drop(columns=["version"]),
                            left_on=col,
                            right_on=col,
                            how="outer",
                        )
                    diff.time_id = pd.to_datetime(diff.time_id)
                    st.session_state[f"diff_{cat}"] = diff

            st.write("対策シナリオセッション準備中")
            prompt = f"""
            event_scenario: {st.session_state.agent["event"]}
            eventの影響
            1. sales: {st.session_state["diff_sales_forecast"]}
            2. resource: {st.session_state["diff_resource_forecast"]}
            3. routing: {st.session_state["diff_routing_forecast"]}
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


left, right = st.columns([0.6, 0.4], vertical_alignment="top")
with right:
    with st.container(border=True, height=800):
        with st.container(border=False, height=60):
            st.subheader(":material/support_agent: Planning Companion", divider="grey")

        chat_history = st.container(border=True, height=630)
        with chat_history:
            for message in st.session_state.agent["chat_history"]:
                with st.chat_message(message["role"]):
                    message["content"]
                    if "fig" in message and message["fig"] is not None:
                        message["fig"]

        with st.container(border=False, height=45):
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
    with st.container(border=True, height=800):
        with st.container(height=95):
            content = st.segmented_control(
                "**描画する資料を選んでください**",
                ["イベント情報", "影響予測　　", "対策情報　　"],
                default="イベント情報",
            )
            if content is None:
                content = "イベント情報"

        report = st.container(height=650)

with report:
    match content:
        case "イベント情報":
            template = st.session_state.jinja.get_template("event.md")
            rdr = template.render(st.session_state.agent["event"])
            st.markdown(rdr)
        case "対策情報　　":
            template = st.session_state.jinja.get_template("strategy.md")
            rdr = template.render(st.session_state.agent["model"].strategy)
            st.markdown(rdr)
        case "影響予測　　":
            cont = st.session_state.agent["event"]
            df = pd.DataFrame(cont["event_cases"]).set_index("version")
            df.columns = cont["event_metrics"].values()
            "##### 比較"
            st.table(df.T)

            field_forecast = st.container()
            with field_forecast:
                cat = st.selectbox("表示するForecastを選んでください", forecasts.keys())
                col = [
                    c
                    for c in forecasts[cat].columns
                    if c
                    not in [
                        "version",
                        "quantity",
                        "cost",
                        "unit_cost",
                    ]
                ]
                c1, c2 = st.columns([3, 1])
                c3, c4 = st.columns(2)
                with c1:
                    c = st.pills("セグメント分析", [c for c in col if c != "time_id"])
                with c2:
                    viz_table = st.toggle("表形式", value=False)
                with c4:
                    ax = [
                        c for c in forecasts[cat].columns if c not in ["version", *col]
                    ]
                    target = "quantity"
                    if len(ax) > 1:
                        target = st.pills("描画対象", ax, default="quantity")
                        target = "quantity" if target is None else target
                with c3:
                    viz_version = st.pills(
                        "比較するversion",
                        ["original", *df.index.unique()],
                        selection_mode="multi",
                    )
                    viz_version = (
                        ["original", *df.index.unique()]
                        if len(viz_version) == 0
                        else viz_version
                    )
                    viz_version = re.compile("(" + "|".join(viz_version) + ")")

                diff = st.session_state[f"diff_{cat}"]

                if c is None:
                    diff = diff.groupby("time_id").sum().reset_index()
                    diff["surrogate"] = "ALL"
                else:
                    diff = diff.groupby(["time_id", c]).sum().reset_index()
                    diff["surrogate"] = diff.loc[:, c]
                diff = diff.drop(columns=[c for c in col if c != "time_id"])

                if viz_table:
                    diff
                else:
                    df = []
                    for a in diff.filter(like=f"{target}_").columns:
                        temp = diff.loc[:, ["time_id", "surrogate", a]].rename(
                            columns={a: target}
                        )
                        temp.surrogate = f"{a}_" + temp.surrogate
                        df.append(temp)
                    sample = pd.concat(df)
                    sample = sample[sample.surrogate.str.contains(viz_version)]
                    st.line_chart(
                        sample,
                        x="time_id",
                        y=target,
                        color="surrogate",
                    )

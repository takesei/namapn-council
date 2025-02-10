import re
from typing import Any, NamedTuple

import pandas as pd
import streamlit as st

from libs.actions import run_action


def initialiaze_forecasts():
    return dict(
        sales_forecast=st.session_state.db.get("sales_forecasts"),
        resource_forecast=st.session_state.db.get("resource_forecasts"),
        routing_forecast=st.session_state.db.get("routing_forecasts"),
    )


def get_forecasts_diff():
    forecasts = initialiaze_forecasts()
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
                    [v for v in fcst.version.unique() if v not in ["V001", "V002"]]
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


class Message(NamedTuple):
    actor: str
    message: str
    attachments: list[Any]


@st.dialog("セッションを開始しますか?")
def start_session():
    c1, c2 = st.columns(2)
    with c1:
        if st.button("はい"):
            provision_data()
    with c2:
        if st.button("いいえ"):
            st.info("待機します, ×ボタンから抜けてください")


def provision_data():
    with st.status("情報取得中"):
        st.write("被害予測取得中")
        get_forecasts_diff()

        st.write("対策シナリオセッション準備中")
        prompt = f"""
        [イベントシナリオ]: {st.session_state.agent["event"]}
        eventの影響
        1. sales: {st.session_state["diff_sales_forecast"]}
        2. resource: {st.session_state["diff_resource_forecast"]}
        3. routing: {st.session_state["diff_routing_forecast"]}
        ユーザーのinput: イベントの概要を説明することを明示した上で3行程度で概要を説明してください.
        また次に何をしたらいいか教えてください
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


def render_agent_interface():
    with st.container(border=True, height=800):
        st.subheader(":material/support_agent: Planning Companion", divider="grey")

        chat_history = st.container(border=True, height=640)
        with chat_history:
            for message in st.session_state.agent["chat_history"]:
                with st.chat_message(message.actor):
                    st.markdown(message.message)
                    for a in message.attachments:
                        run_action(a)

        if prompt := st.chat_input("What is up?"):
            st.session_state.agent["chat_history"].append(
                Message(actor="user", message=prompt, attachments=[])
            )
            with chat_history:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    try:
                        resp = st.session_state.agent["model"].send_message(prompt)
                        st.write(resp.message)
                        run_action(resp.actions)
                        cont = Message(
                            actor="assistant",
                            message=resp.message,
                            attachments=resp.actions,
                        )
                    except Exception as e:
                        st.error(e)
                        cont = Message(
                            actor="assistant",
                            message=f"error: {e}",
                            attachments=[],
                        )
                    st.session_state.agent["chat_history"].append(cont)


def render_report_renderer():
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

                    st.markdown("##### 比較")
                    st.table(df.T)

                    field_forecast = st.container()
                    with field_forecast:
                        forecasts = initialiaze_forecasts()
                        cat = st.selectbox(
                            "表示するForecastを選んでください", forecasts.keys()
                        )
                        col = [
                            c
                            for c in forecasts[cat].columns
                            if c not in ["version", "quantity", "cost", "unit_cost"]
                        ]
                        c1, c2 = st.columns([3, 1])
                        c3, c4 = st.columns(2)
                        with c1:
                            c = st.pills(
                                "セグメント分析", [c for c in col if c != "time_id"]
                            )
                        with c2:
                            viz_table = st.toggle("表形式", value=False)
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

                        with c4:
                            ax = [
                                c
                                for c in forecasts[cat].columns
                                if c not in ["version", *col]
                            ]
                            target = "quantity"
                            if len(ax) > 1:
                                target = st.pills("描画対象", ax, default="quantity")
                                target = "quantity" if target is None else target

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


# UI
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
    render_agent_interface()

with left:
    render_report_renderer()

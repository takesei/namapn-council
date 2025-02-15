import streamlit as st
from modules.top.contingency_plan.companion import Message
import pandas as pd
from libs.typing import Forecasts


def get_forecasts_diff(forecasts: Forecasts):
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


def provision_data(forecasts: Forecasts):
    with st.status("情報取得中"):
        st.write("被害予測取得中")
        get_forecasts_diff(forecasts)

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

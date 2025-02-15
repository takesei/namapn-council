from jinja2 import Environment, Template

import pandas as pd
import streamlit as st

from libs.typing import JSON, EventScenario, StrategyScenario, Forecasts


def render_event_influence(event_scenario: EventScenario):
    case_comparison_container = st.container()
    forecast_container = st.container()

    with case_comparison_container:
        df_cases = (
            pd.DataFrame(event_scenario.event_cases, columns=event_scenario.event_cases)
            .set_index("version")
            .T
        )
        st.markdown("##### 比較")
        st.table(df_cases)

    with forecast_container:
        render_forecasts_container()


def render_report(
    jinja_env: Environment,
    event_scenario: EventScenario,
    strategy_scenario: StrategyScenario,
    forecasts: Forecasts,
):
    report_seelctor_container = st.container(height=95)
    report_container = st.container(height=650)

    with report_seelctor_container:
        report = render_report_selector()

    with report_container:
        match report:
            case "イベント情報":
                render_event_influence(event_scenario)
            case "対策情報　　":
                template = jinja_env.get_template("strategy.md")
                render_template(template, strategy_scenario)
            case "影響予測　　":
                template = jinja_env.get_template("event.md")
                render_template(template, event_scenario)


def render_report_selector():
    if content := st.segmented_control(
        "**描画する資料を選んでください**",
        ["イベント情報", "影響予測　　", "対策情報　　"],
        default="イベント情報",
    ):
        return content
    else:
        return "イベント情報"


def render_template(template: Template, content: JSON):
    rdr = template.render(content)
    st.markdown(rdr)


def render_forecasts_container(df_cases: pd.DataFrame, forecasts: Forecasts):
    name = st.selectbox("表示するForecastを選んでください", forecasts.contents())
    segments = forecasts[name].segments
    values = forecasts[name].values
    df_diff = forecasts[name].diff
    df_summary = None

    c1, c2 = st.columns([3, 1])
    c3, c4 = st.columns(2)

    with c1:
        c = st.pills("セグメント分析", segments)
    with c2:
        viz_table = st.toggle("表形式", value=False)
    with c3:
        all_cases = ["original", *df_cases.columns]
        viz_version = st.pills("比較するversion", all_cases, selection_mode="multi")
        if len(viz_version) == 0:
            viz_version = all_cases
    with c4:
        target = st.pills("描画対象", values, default=values[0])
        if target is None:
            target = values[0]

    if c is None:
        df_summary = df_diff.groupby("time_id").sum().reset_index()
        df_summary["surrogate"] = "ALL"
    else:
        df_summary = df_diff.groupby(["time_id", c]).sum().reset_index()
        df_summary["surrogate"] = df_summary.loc[:, c]
    df_summary = df_summary.drop(columns=[c for c in segments])

    if viz_table:
        df_summary
    else:
        df = []
        for a in df_summary.filter(like=f"{target}_").columns:
            temp = df_summary.loc[:, ["time_id", "surrogate", a]].rename(
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

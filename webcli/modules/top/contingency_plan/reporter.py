from jinja2 import Environment, Template

import pandas as pd
import streamlit as st

from libs.typing import JSON, EventScenario, StrategyScenario
from libs.datahub import DataHub


def render_event_influence(event_scenario: EventScenario, forecasts):
    case_comparison_container = st.container()
    forecast_container = st.container()

    with case_comparison_container:
        df_cases = pd.DataFrame(event_scenario.event_cases).set_index("version").T
        st.markdown("##### 比較")
        st.table(df_cases)

    with forecast_container:
        render_forecasts_container(df_cases, forecasts)


def render_report(
    jinja_env: Environment,
    event_scenario: EventScenario,
    strategy_scenario: StrategyScenario,
    datahub: DataHub,
):
    report_seelctor_container = st.container(height=95)
    report_container = st.container(height=650)

    with report_seelctor_container:
        report = render_report_selector()

    with report_container:
        match report:
            case "イベント情報":
                template = jinja_env.get_template("event.md")
                render_template(template, event_scenario.to_dict())
            case "影響予測　　":
                render_event_influence(event_scenario, datahub)
            case "対策情報　　":
                template = jinja_env.get_template("strategy.md")
                render_template(template, strategy_scenario.to_dict())


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


def render_forecasts_container(df_cases: pd.DataFrame, datahub: DataHub):
    name = st.selectbox("表示するForecastを選んでください", datahub.contents())
    segments = datahub[name].segments
    values = datahub[name].values
    df_summary = None

    c1, c2 = st.columns([3, 1])
    c3, c4 = st.columns(2)

    with c1:
        c = st.pills("セグメント分析", segments)
        if c is None:
            c = []
    with c2:
        viz_table = st.toggle("表形式", value=False)
    with c3:
        all_cases = ["V001", *df_cases.columns]
        viz_version = st.pills("比較するversion", all_cases, selection_mode="multi")
        if len(viz_version) == 0:
            viz_version = all_cases
    with c4:
        target = st.pills("描画対象", values, default=values[0])
        if target is None:
            target = values[0]

    try:
        df_diff = datahub[name].diff(
            target_versions=viz_version, segments=c, values=target
        )
        df_summary = df_diff.drop(columns=c)

        if viz_table:
            st.dataframe(df_summary)
        else:
            st.line_chart(
                df_summary,
                x="time_id",
                y=df_summary.filter(like=f"{target}").columns,
                color="label",
            )
    except Exception as e:
        st.error(f"Table {name} doesn't support version comparison")
        print(e)

import streamlit as st
from libs.actions import run_action
import pandas as pd


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


# if st.session_state.agent["event"] is None:
#     st.info("重要なイベントはありません")
#     st.stop()
# if st.session_state.agent["status"] == "deactive":
#     "# イベント対応"
#     st.warning("**イベントを検知しました, 開始ボタンから状況を開始してください**")
#     if st.button("状況を開始"):
#         start_session()
#     st.stop()


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
            c1, c2 = st.columns([3, 1])
            with c1:
                content = st.segmented_control(
                    "**描画する資料を選んでください**",
                    ["イベント情報", "対策情報　　"],
                    default="イベント情報",
                )
                if content is None:
                    content = "イベント情報"
            with c2:
                is_bi = st.toggle("BIモード", value=True)

        with st.container(height=650):
            match content:
                case "イベント情報":
                    if is_bi:
                        cont = st.session_state.agent["event"]
                        refs = [
                            f"  - [{ref}](https://google.com)"
                            for ref in [
                                *cont["past_incidents"],
                                cont["related_manuals"],
                                cont["real_time_info"],
                            ]
                        ]
                        refs = ("\n  " + " " * 24) + ("\n  " + " " * 24).join(refs)
                        f"""
                        ### [{cont["version"]}版] {cont["incident_name"]}
                        - 発行日: {cont["issue_date"]}
                        - 深刻度: **{cont["severity"]}**
                        - 発行者: {cont["responsible_person"]} ({cont["department"]})
                        - 参考情報: {refs}
                        """

                        """
                        #### 状況変化予測
                        """
                        st.dataframe(pd.DataFrame(cont["timeline"]), hide_index=True)

                        "#### 影響予測"
                        case = cont["impact_details"].keys()
                        prob = cont["impact_probabilities"].values()
                        detail = [", ".join(e) for e in cont["impact_details"].values()]
                        proc = cont["affected_business_processes"].values()
                        df = pd.DataFrame(
                            [prob, detail, proc],
                            columns=["V003", "V004"],
                            index=["確率", "概要", "影響"],
                        ).T

                        forecasts = dict(
                            sales=st.session_state.db.get("sales_forecasts"),
                            resource=st.session_state.db.get("resource_forecasts"),
                            routing=st.session_state.db.get("routing_forecasts"),
                        )

                        for case, (version, row) in zip(case, df.iterrows()):
                            with st.container(border=True):
                                f"##### Case: {case} (version_id = {version})"
                                row
                                with st.expander("###### Forecastへの影響"):
                                    for cat, fcst in forecasts.items():
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
                                        ord = fcst[fcst.version == "V001"].drop(
                                            columns=["version"]
                                        )
                                        evt = fcst[fcst.version == version].drop(
                                            columns=["version"]
                                        )
                                        f"###### {cat} forecast"
                                        diff = pd.merge(
                                            ord,
                                            evt,
                                            left_on=col,
                                            right_on=col,
                                            how="outer",
                                            suffixes=["_ordinal", "_event"],
                                        )
                                        diff.time_id = pd.to_datetime(diff.time_id)
                                        col.remove("time_id")
                                        c1, c2 = st.columns([3, 1])
                                        with c1:
                                            c = st.pills(
                                                "集計する属性",
                                                col,
                                                key=f"event_bi_groupby_{cat}_{version}",
                                            )
                                        with c2:
                                            viz_table = st.toggle(
                                                "表形式",
                                                value=False,
                                                key=f"event_bi_viz_{cat}_{version}",
                                            )

                                        if c is None:
                                            diff = (
                                                diff.groupby("time_id")
                                                .sum()
                                                .reset_index()
                                            )
                                            diff["surrogate"] = "ALL"
                                            diff = diff.drop(columns=col)
                                        else:
                                            diff = (
                                                diff.groupby(["time_id", c])
                                                .sum()
                                                .reset_index()
                                            )
                                            diff["surrogate"] = diff.loc[:, c]
                                            diff = diff.drop(columns=col)
                                        if viz_table:
                                            diff
                                        else:
                                            ax = [
                                                c
                                                for c in diff.columns
                                                if c not in ["time_id", "surrogate"]
                                            ]
                                            target = "quantity"
                                            if len(ax) > 2:
                                                _ax = {a.split("_")[0] for a in ax}
                                                target = st.pills(
                                                    "描画対象",
                                                    _ax,
                                                    key=f"event_axis_viz_{cat}_{version}",
                                                    default="quantity",
                                                )
                                                if target is None:
                                                    target = "quantity"
                                            df = []
                                            for a in ax:
                                                temp = diff.loc[
                                                    :, ["time_id", "surrogate", a]
                                                ].rename(columns={a: target})
                                                temp.surrogate = (
                                                    f"{a}_" + temp.surrogate
                                                )
                                                df.append(temp)
                                            sample = pd.concat(df)
                                            sample = sample[
                                                sample.surrogate.str.startswith(target)
                                            ]
                                            st.line_chart(
                                                sample,
                                                x="time_id",
                                                y=target,
                                                color="surrogate",
                                            )
                    else:
                        template = st.session_state.jinja.get_template("event.md")
                        rdr = template.render(st.session_state.agent["event"])
                        st.markdown(rdr)
                case "対策情報　　":
                    template = st.session_state.jinja.get_template("strategy.md")
                    rdr = template.render(st.session_state.agent["model"].strategy)
                    st.markdown(rdr)

import streamlit as st
import pandas as pd

"""
# Monitor room
"""

if st.session_state.event is not None:
    st.toast("[**緊急**] 緊急計画pageを確認ください", icon="⚠️")

with st.spinner():
    v_ax = st.session_state.db.get("versions")
    v_ax = v_ax[v_ax.is_active].sort_values("version_code").reset_index(drop=True)
    tag = v_ax.version_code + ":" + v_ax.version_name
    version = st.pills("指定バージョン", tag, selection_mode="single", default=tag[0])
    version = version.split(":")[0]

    upper = st.columns(2)
    lower = st.columns(2)

    with upper[1]:
        with st.container(border=True, height=500):
            "**粗利速報**"
            tran = st.session_state.db.get("transactions")
            so = tran.loc[
                (tran.version == version) & (tran.transaction_type == "Sales"),
                ["time_id", "price", "quantity"],
            ]
            so = (
                so.assign(sales=so.price * so.quantity)
                .loc[:, ["time_id", "sales"]]
                .groupby("time_id")
                .sum()
                .reset_index()
            )
            po = tran.loc[
                (tran.version == version) & (tran.transaction_type == "Purchase"),
                ["time_id", "price", "quantity"],
            ]
            po = (
                po.assign(material_cost=po.price * po.quantity)
                .loc[:, ["time_id", "material_cost"]]
                .groupby("time_id")
                .sum()
                .reset_index()
            )
            df = pd.merge(so, po, left_on="time_id", right_on="time_id", how="outer")
            df = df.assign(gross_profit=df.sales - df.material_cost)
            df.time_id = pd.to_datetime(df.time_id).dt.strftime("%Y/%m/%d")
            st.line_chart(df, x="time_id", y=["material_cost", "sales", "gross_profit"])

    with upper[0]:
        with st.container(border=True, height=500):
            "**指標**"
            ratio = (df.gross_profit / df.sales) * 100
            delta = ratio.iloc[-1] - ratio.iloc[0]
            c1, c2 = st.columns(2, border=True)
            c3, c4 = st.columns(2, border=True)
            with c1:
                st.metric(
                    "粗利",
                    f"{df.gross_profit.mean():.2f}",
                    delta=f"{df.gross_profit.iloc[-1] - df.gross_profit.iloc[0]:.2f}",
                )
            with c2:
                st.metric("粗利率", f"{ratio.mean():.2f}%", delta=f"{delta:.2f}%")

            with c4:
                f"""**current base scenario**  
                **{version}**
                """

    with lower[0]:
        with st.container(border=True, height=500):
            "**製造/販売 マッチング率**"
            sal = st.session_state.db.get("sales_forecasts")
            prd = st.session_state.db.get("production_forecasts")

            with st.container(border=True, height=95):
                sample = st.pills(
                    "item_id",
                    pd.Series(["ALL", *sal.item_code, *prd.item_code])
                    .sort_values()
                    .unique(),
                    default="ALL",
                )

            if sample != "ALL":
                sal_cond = (sal.version == version) & (sal.item_code == sample)
                prd_cond = (prd.version == version) & (prd.item_code == sample)
            else:
                sal_cond = sal.version == version
                prd_cond = prd.version == version
            sal = (
                sal.loc[
                    sal_cond,
                    ["time_id", "quantity", "item_code"],
                ]
                .rename(columns=dict(quantity="sales_quantity"))
                .groupby(["time_id", "item_code"])
                .sum()
                .reset_index()
            )
            prd = (
                prd.loc[
                    prd_cond,
                    ["time_id", "quantity", "item_code"],
                ]
                .rename(columns=dict(quantity="production_quantity"))
                .groupby(["time_id", "item_code"])
                .sum()
                .reset_index()
            )

            sal.time_id = pd.to_datetime(sal.time_id)
            prd.time_id = pd.to_datetime(prd.time_id)

            df = pd.merge(
                sal,
                prd,
                left_on=["time_id", "item_code"],
                right_on=["time_id", "item_code"],
                how="outer",
            )
            if sample == "ALL":
                df = df.groupby(["time_id"]).sum().reset_index()
            df = df.drop(columns=["item_code"])
            df.time_id = df.time_id.dt.strftime("%Y/%m/%d")

            st.bar_chart(
                df,
                x="time_id",
                stack=False,
            )
            with c3:
                ratio = df.production_quantity / df.sales_quantity * 100
                st.metric(
                    "製造量販売量比率",
                    f"{ratio.mean():.2f}%",
                    delta=f"{ratio.iloc[-1] - ratio.iloc[0]:.2f}%",
                )

    with lower[1]:
        with st.container(border=True, height=500):
            "**今後の売れ行き予想**"
            df = st.session_state.db.get("sales_forecasts")
            seg = st.segmented_control(
                "セグメント",
                ["item_code", "company_code", "customer_code"],
                default="item_code",
            )
            default_col = ["time_id", "quantity"]
            col = default_col if seg is None else [seg, *default_col]
            df = df.loc[df.version == version, col]
            df.time_id = pd.to_datetime(df.time_id).dt.date
            df = df.groupby(col[:-1]).mean().reset_index()

            st.line_chart(
                df,
                x="time_id",
                y="quantity",
                color=seg,
                x_label="日付",
                use_container_width=True,
            )

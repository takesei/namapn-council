from typing import Any
import pandas as pd
from io import StringIO
import streamlit as st


def run_action(infos: list[dict[str, Any]]):
    for info in infos:
        if info.action_type == "plot":
            arg = info.keyword_arguments
            src = pd.read_json(StringIO(arg["source"]))
            plot_type = arg["plot_type"]
            if plot_type == "line":
                try:
                    st.line_chart(
                        data=src,
                        x=arg["x"],
                        y=arg["y"],
                        color=input["color"] if "color" in input else None,
                    )
                except Exception as e:
                    st.dataframe(StringIO(arg["source"]))
                    print(e)
            elif plot_type == "bar":
                try:
                    st.bar_chart(
                        data=src,
                        x=arg["x"],
                        y=arg["y"],
                        color=input["color"] if "color" in input else None,
                    )
                except Exception as e:
                    st.dataframe(StringIO(arg["source"]))
                    print(e)
            else:
                st.dataframe(src)

from typing import Any
import pandas as pd
from io import StringIO
import streamlit as st


def run_action(infos: list[dict[str, Any]]):
    for info in infos:
        print(f"got {info}")
        if info["type"] == "plot":
            input = info["input"]
            if input["plot_type"] == "line":
                st.line_chart(
                    data=pd.read_json(StringIO(input["source"])),
                    x=input["x"],
                    y=input["y"],
                )
            elif input["plot_type"] == "bar":
                st.bar_chart(
                    data=pd.read_json(StringIO(input["source"])),
                    x=input["x"],
                    y=input["y"],
                )
            else:
                return None

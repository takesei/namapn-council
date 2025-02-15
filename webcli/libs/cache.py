from importlib import resources

import streamlit as st
import tomllib
import yaml
from jinja2 import Environment, FileSystemLoader

from libs.genai import StrategyMaker
from libs.store import DataCatalog


@st.cache_data(show_spinner=True, persist=False)
def load_navigation():
    print("Load TOML File")
    with open("navigation.toml", "rb") as f:
        pages = tomllib.load(f)

    return {
        section_name: [st.Page(**attr) for attr in page_attrs]
        for section_name, page_attrs in pages.items()
    }


@st.cache_resource
def setup_aiagent():
    print("Create Gemiin Agent")
    empty_scenario = {
        "strategy_name": "",
        "strategy_id": "",
        "create_date": "",
        "version": "",
        "department": "",
        "responsible_person": "",
        "event": {"impact_level": "", "version": "", "name": "", "url": ""},
        "activation": {
            "responsible": "",
            "time": "",
            "conditions": "",
            "metrics": [],
            "notifications": [],
        },
        "initial_response": [],
        "containment_measures": [],
        "monitoring": [],
        "recovery": [],
    }

    return dict(
        model=StrategyMaker(),
        chat_history=[],
        event=None,
        status="deactive",
    )


@st.cache_resource
def set_template(path: str):
    print("Load Templates")
    env = Environment(loader=FileSystemLoader(path), trim_blocks=True)
    return env


@st.cache_resource
def get_data_catalog(db: str):
    print("Create DB Session")
    file_path = resources.files("libs.tables").joinpath("schema.yml")
    with file_path.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)["mart"]
    catalog = DataCatalog(db, schema)

    return catalog

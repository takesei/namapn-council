import streamlit as st
import tomllib
from jinja2 import Environment, FileSystemLoader
import yaml

from genai import ScenarioMaker

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
        model=ScenarioMaker(empty_scenario),
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
    with open("libs/tables/schema.yml", "r") as f:
        schema = yaml.safe_load(f)["mart"]
    catalog = DataCatalog(db, schema)

    return catalog

import streamlit as st
import vertexai
import tomllib
import duckdb
import os

from genai import ScenarioMaker

# Page Config
st.set_page_config(
    page_title="Namaph Council Demo",
    page_icon=":material/forest:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Load Navigation config
@st.cache_data(show_spinner=True, persist=False)
def load_navigation():
    print("Load TOML File")
    with open("navigation.toml", "rb") as f:
        pages = tomllib.load(f)

    return {
        section_name: [st.Page(**attr) for attr in page_attrs]
        for section_name, page_attrs in pages.items()
    }


pages = load_navigation()

# Init ai connection
vertexai.init(project="velvety-outcome-448307-f0", location="us-central1")


@st.cache_resource
def connect_gemini_agent():
    print("Create Gemiin Agent")
    agent = ScenarioMaker()

    return agent


if "aiagent" not in st.session_state:
    st.session_state.aiagent = connect_gemini_agent()
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_ai_last_msg" not in st.session_state:
    st.session_state.agent_ai_last_msg = (
        "過去の履歴はありません, これが最初のやりとりです."
    )

if "strategy_scenario" not in st.session_state:
    st.session_state.strategy_scenario = {}


# Create DB connection
@st.cache_resource
def duckdb_local_session(db: str):
    print("Create DB Session")
    con = duckdb.connect(database=db)

    return con


def fetch_data():
    # BQからimpactの情報を取ってくる。今は擬似的に全部ローカルに置いている。
    impact = """
    ---今回の影響範囲
    以下が調達計画の影響範囲です。
    顧客ID	製品名	月	元の計画名	元の計画値	被害予測名	被害予測の値	影響量
    C001	I012	5	ordinal	20000	pred_kansai	10000	-10000
    C001	I012	4	ordinal	20000	pred_kansai	10000	-10000
    C001	I010	4	ordinal	40000	pred_kansai	20000	-20000
    C001	I010	5	ordinal	40000	pred_kansai	20000	-20000
    C001	I011	5	ordinal	10000	pred_kansai	5000	-5000
    C001	I013	5	ordinal	10000	pred_kansai	5000	-5000
    C001	I013	4	ordinal	10000	pred_kansai	5000	-5000
    C001	I011	4	ordinal	10000	pred_kansai	5000	-5000
    """

    # 不測の事態が発生した時の初期対応を行う場合に呼び出される
    # from bq
    event_scenario = """
    {"incident_name":"2025年9月14日台風直撃による影響","incident_id":"20250914_Typhoon","issue_date":"2025/09/1312:00","version":"V1.3","department":"危機管理部門","responsible_person":"田中一郎","incident_date":"2025/09/1412:00","duration":"2025/09/1412:00〜2025/09/1623:59","evidence":"気象庁発表（2025/09/1308:00）","past_incidents":["2023年台風12号（物流停止による在庫逼迫）"],"severity":"重大","impact_probabilities":{"関西圏直撃":75,"九州直撃":20},"impact_details":{"関西":["物流停止による原材料供給不足","調達計画の見直しが必要"],"九州":["リテールの物流網が停止","販売機会の損失"]},"affected_business_processes":{"関西圏影響":"調達部門の原材料確保が困難、工場生産ラインの調整が必要","九州圏影響":"販売部門のリテール配送が停止、在庫逼迫により販売調整が必要"},"estimated_loss":"1.2億円","delivery_impact":"主要取引先5社に影響","timeline":[{"time":"09/13深夜","status":"台風進路確定","impact":"関西か九州のどちらかが確定する"},{"time":"09/14昼","status":"台風直撃","impact":"物流網停止、業務への影響開始"},{"time":"09/14夕方","status":"影響継続","impact":"物流・リテール停止、代替策の実施が必要"},{"time":"09/15","status":"影響収束","impact":"復旧作業・業務調整開始"}],"damage_control_scenarios":["関西シナリオ（調達影響）","九州シナリオ（販売影響）"],"related_manuals":"台風対応マニュアルv2.1","real_time_info":"気象庁のリアルタイム台風情報"}
    """

    prompt = f"""
    イベントの詳細: {event_scenario}
    イベントの被害: {impact}
    ユーザーのinput: イベントが発生しました, 次に何をしたらいいか教えてください
    """
    response = st.session_state.aiagent.send_message(
        prompt,
        st.session_state.strategy_scenario,
        st.session_state.agent_ai_last_msg,
    )
    st.session_state.messages.append(
        {"role": "assistant", "content": response["msg"], "fig": None}
    )
    st.session_state.agent_ai_last_msg = response["msg"]
    st.session_state.strategy_scenario = response["strategy"]


if "db" not in st.session_state:
    st.session_state.db = duckdb_local_session("./dwh.duckdb")

if "data_fetched" not in st.session_state:
    print("Fetch data")
    os.makedirs("data", exist_ok=True)
    msg = st.toast("データ更新中", icon=":material/sync:")
    err = fetch_data()
    if err is None:
        msg.toast("データ更新完了, good luck!!", icon=":material/check:")
        st.session_state.data_fetched = True
    else:
        msg.toast("データ更新失敗, try again later", icon=":material/block:")

# Navigation
pg = st.navigation(pages)

with st.sidebar:
    with st.container(border=True):
        st.error("**緊急対応**", icon="⚠️")
        st.page_link(
            "./modules/top/contingency_plan.py",
            label="台風上陸による調達計画影響",
        )

pg.run()

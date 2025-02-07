import duckdb
import json
import requests
import io
import pandas as pd


def access_bq(table_uri: str):
    url = "https://execute-bq-query-42822254114.us-west1.run.app"
    query = f"select * from {table_uri}"
    print(query)
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={"query": query},
        timeout=10,
    )

    response.raise_for_status()
    data = response.json()["data"]
    df = pd.read_json(io.StringIO(data))
    return df


class DataCatalog:
    conn: duckdb.duckdb.DuckDBPyConnection
    fetch_list: dict[str, bool]

    def __init__(self, db: str, schema: dict[str, dict[str, str]]) -> None:
        # self.master_list = [e["name"] for e in schema["master"]]
        self.schema = schema
        self.mart_list = (
            sum(list(schema["dimension"].values()), [])
            + schema["forecast"]
            + schema["transaction"]
        )
        print(self.mart_list)
        self.conn = duckdb.connect(database=db)
        self.local_table = []

    def get(self, table: str) -> pd.DataFrame:
        # TODO: Temporary implement
        if table == "event_scenario":
            return json.loads(
                '{"event_name":"台風15号直撃の可能性","event_id":"20250914_Typhoon","issue_date":"2025-09-13T12:00:00Z","version":"V1.3","department":"経営企画部","responsible_person":"田中一郎","impact_level":"重大","overview":"台風が関西圏または九州圏に直撃し、物流・調達および販売に影響を及ぼす可能性がある。","impact_duration":{"start":"2025-09-14T12:00:00Z","end":"2025-09-16T23:59:00Z"},"event_metrics":{"name":"名称","probability":"発生する確率","overview":"影響の概要","process":"影響を受けるプロセス","risk":"KPIへの影響"},"event_cases":[{"version":"V003","name":"関西直撃","probability":"75%","overview":"物流停止による原材料供給不足","process":"調達部門の原材料確保が困難、工場生産ラインの調整が必要","risk":"予測売上損失1.2億円、主要取引先5社に影響"},{"version":"V004","name":"九州直撃","probability":"20%","overview":"リテールの物流網が停止し、販売機会の損失","process":"販売部門のリテール配送が停止、在庫逼迫により販売調整が必要","risk":"販売停止により九州全域での売上減少が懸念される"}],"timeline":[{"time":"2025-09-13T23:00:00Z","status":"台風進路確定","impact":"関西か九州のどちらかが確定する"},{"time":"2025-09-14T12:00:00Z","status":"台風直撃","impact":"物流網停止、業務への影響開始"},{"time":"2025-09-14T18:00:00Z","status":"影響継続","impact":"物流・リテール停止、代替策の実施が必要"},{"time":"2025-09-15T00:00:00Z","status":"影響収束","impact":"復旧作業・業務調整開始"}],"evidences":[{"name":"気象庁発表","url":"https://www.jma.go.jp/"}],"references":[{"name":"2023年台風12号の影響分析","url":"https://example.com/typhoon-2023"},{"name":"事業継続計画（BCP）ガイドライン","url":"https://example.com/bcp-guidelines"},{"name":"台風対応マニュアルv2.1","url":"https://google.com"},{"name":"気象庁のリアルタイム台風情報","url":"https://google.com"},{"name":"2023年台風12号イベントシナリオ","url":"https://example.com/typhoon-2023"}]}'
            )
        if table in self.local_table:
            return self.conn.sql(f"select * from {table}").df()

        elif table in self.mart_list:
            df = access_bq(f"mart.{table}")
            self.conn.execute(f"CREATE OR REPLACE TABLE {table} as select * from df")
            self.local_table.append(table)
            return df
        else:
            raise RuntimeError(f"table {table} not found")

    def set_local(self, table: str, df: pd.DataFrame) -> None:
        self.conn.execute(f"CREATE OR REPLACE TABLE {table} as select * from df")
        if table not in self.local_table:
            self.local_table.append(table)

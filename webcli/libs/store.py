import duckdb
import json
import requests
import io
import pandas as pd


class DataCatalog:
    conn: duckdb.duckdb.DuckDBPyConnection
    fetch_list: dict[str, bool]

    def __init__(self, db: str) -> None:
        self.conn = duckdb.connect(database=db)
        self.fetch_list = dict(
            bom_trees=False,
            companies=False,
            customers=False,
            dates=False,
            finished_goods=False,
            item_types=False,
            items=False,
            lines=False,
            locations=False,
            materials=False,
            months=False,
            plants=False,
            production_forecasts=False,
            resource_forecasts=False,
            retailers=False,
            routing=False,
            routing_forecasts=False,
            routings=False,
            sales_forecasts=False,
            storages=False,
            suppliers=False,
            times=False,
            transaction_types=False,
            transactions=False,
            versions=False,
            years=False,
        )

    def get(self, table: str) -> pd.DataFrame:
        if table == "event_scenario":
            return json.loads(
                '{"incident_name":"2025年9月14日台風直撃による影響","incident_id":"20250914_Typhoon","issue_date":"2025/09/1312:00","version":"V1.3","department":"危機管理部門","responsible_person":"田中一郎","incident_date":"2025/09/1412:00","duration":"2025/09/1412:00〜2025/09/1623:59","evidence":"気象庁発表（2025/09/1308:00）","past_incidents":["2023年台風12号（物流停止による在庫逼迫）"],"severity":"重大","impact_probabilities":{"関西圏直撃":75,"九州直撃":20},"impact_details":{"関西":["物流停止による原材料供給不足","調達計画の見直しが必要"],"九州":["リテールの物流網が停止","販売機会の損失"]},"affected_business_processes":{"関西圏影響":"調達部門の原材料確保が困難、工場生産ラインの調整が必要","九州圏影響":"販売部門のリテール配送が停止、在庫逼迫により販売調整が必要"},"estimated_loss":"1.2億円","delivery_impact":"主要取引先5社に影響","timeline":[{"time":"09/13深夜","status":"台風進路確定","impact":"関西か九州のどちらかが確定する"},{"time":"09/14昼","status":"台風直撃","impact":"物流網停止、業務への影響開始"},{"time":"09/14夕方","status":"影響継続","impact":"物流・リテール停止、代替策の実施が必要"},{"time":"09/15","status":"影響収束","impact":"復旧作業・業務調整開始"}],"damage_control_scenarios":["関西シナリオ（調達影響）","九州シナリオ（販売影響）"],"related_manuals":"台風対応マニュアルv2.1","real_time_info":"気象庁のリアルタイム台風情報"}'
            )
        elif table == "impact":
            return """
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

        if table not in self.fetch_list:
            raise KeyError(f"table name {table} not found")

        if self.fetch_list[table]:
            return self.conn.sql(f"select * from {table}").df()
        else:
            # Endpoint of Cloud Functions
            url = "https://execute-bq-query-42822254114.us-west1.run.app"

            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"query": f"select * from master_data.{table}"},
                timeout=10,
            )

            response.raise_for_status()
            data = response.json()["data"]
            df = pd.read_json(io.StringIO(data))
            self.conn.execute(f"CREATE OR REPLACE TABLE {table} as select * from df")
            self.fetch_list[table] = True
            return df

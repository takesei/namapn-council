from vertexai.generative_models import (
    GenerativeModel,
)
import traceback

from libs import functions as F
from libs.typing import ProcessCaller

from libs.genai.agent import AgentResponse
from libs.genai.loader import load_config_as_gemini_agent

import json


class InsightAgent:
    model: GenerativeModel
    interpreter: GenerativeModel

    def __init__(self) -> None:
        self.model = load_config_as_gemini_agent(
            "libs.genai.strategy_agent.config.insight"
        )
        self.interpreter = load_config_as_gemini_agent(
            "libs.genai.strategy_agent.config.interpreter"
        )

    def send_message(self, prompt: str) -> AgentResponse[ProcessCaller]:
        """
        任意のタイミングで実行できる, データベース(BigQuery)へアクセスして情報を取得する関数
        ユーザーからデータに関する質問を受けた場合に積極的に選択する。
        プロンプトを元に、text-to-SQLを実行し, 生成されたクエリに対応するデータを取得する
        データを調べる必要があるようなものがあったときにはこれを適用する。

        Args:
            prompt: str ユーザからどう言ったデータをとってきて欲しいかの指示
                    調べるべきデータの内容を日本語で詳細に記載してください。

        Returns: ScenarioMakerResponse
            ScenarioMakerResponse.msg: データの解釈
            ScenarioMakerResponse.strategy: 最新の対策シナリオ
            ScenarioMakerResponse.actions: 得られたデータと, 描画の仕方の方法の提示
        """
        print("===RUN INSIGHT===")
        resp = self.model.generate_content(prompt)
        query = json.loads(resp.text)
        print("thinking: " + query["thinking"])
        try:
            dataframe_json = F.run_bq_query(query["query"])
        except Exception as e:
            print(e)
            traceback.print_exc()
        info = self.interpreter.generate_content(
            f"dataframe: {dataframe_json}\nprompt: {prompt}"
        )

        x = info["x"] if info["x"] != "NULL" else None
        y = info["y"] if info["y"] != "NULL" else None

        message = info["interpretation"]

        print("===DONE===")
        return AgentResponse(
            message=message,
            attachments=ProcessCaller(
                "plot",
                dict(source=dataframe_json, plot_type=info["plot_type"], x=x, y=y),
            ),
        )

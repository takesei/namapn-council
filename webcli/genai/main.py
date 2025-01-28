from typing import Any, Generator
import json
import requests
from vertexai.generative_models import (
    GenerativeModel,
    ChatSession,
)

from .models import txt2sql_conf, interpreter_conf


class GeminiAgent:
    model: GenerativeModel
    worker_models: dict[str, GenerativeModel]

    chat_session: ChatSession | None

    def __init__(self):
        # self.model = GenerativeModel(**manager_conf)
        self.worker_models = dict(
            txt2sql=GenerativeModel(**txt2sql_conf),
            interpreter=GenerativeModel(**interpreter_conf),
        )
        self.chat_session = None

    def send_message(self, prompt: str, **config: Any) -> Generator[str] | str:
        if self.chat_session is None:
            self.chat_session = self.model.start_chat()

        response = self.chat_session.send_message(prompt, stream=False, **config)
        return response.text

    def send_message_streaming(
        self, prompt: str, **config: Any
    ) -> Generator[str] | str:
        if self.chat_session is None:
            self.chat_session = self.model.start_chat()

        for chunk in self.chat_session.send_message(prompt, stream=True, **config):
            yield chunk.text

    def generate_plot(self, prompt: str):
        """プロンプトを元に、text-to-SQLを実行しパースされたデータを取得する"""
        query = self.run_worker_agent("txt2sql", prompt)
        dataframe_json = self.run_query(query["query"])
        info = self.run_worker_agent("interpreter", dataframe_json)

        output_json = {
            "msg": info["interpretation"],
            "actions": [
                {
                    "type": "plot",
                    "input": {
                        # data_dictなど、実際にplotlyで使いたい形式に応じて
                        "source": dataframe_json,
                        "plot_type": info["plot_type"],
                        "x_axis": info["x_axis"],
                        "y_axis": info["y_axis"],
                    },
                }
            ],
        }
        return output_json

    def run_worker_agent(self, worker_name: str, prompt: str):
        model = self.worker_models[worker_name]
        content = model.generate_content(prompt, stream=False).text

        # JSON文字列をパース
        try:
            data = json.loads(content)  # JSONを辞書に変換
        except json.JSONDecodeError as e:
            print(f"JSONのパースに失敗しました: {e}")
        except KeyError as e:
            print(f"キー '{e}' が存在しません。")

        return data

    def run_query(self, query: str) -> str:
        """デプロイ済みの Cloud Run/Functions を呼び出すための関数"""

        print("Query from LLM")
        print(query)
        print("==============\n")

        # Endpoint of Cloud Functions
        url = "https://execute-bq-query-42822254114.us-west1.run.app"

        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={"query": query},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return response.text if data is None else data["data"]

        else:
            raise RuntimeError(
                f"Error: status code {response.status_code}, body={response.text}"
            )

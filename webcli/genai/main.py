from vertexai.generative_models import (
    GenerativeModel,
    ChatSession,
)

import json
from typing import Any
from .agent import GeminiAgent
from .models import txt2sql_conf, interpreter_conf, facilitator_conf, organizer_conf
from . import functions as F

JSON: type = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


class ScenarioMaker(GeminiAgent):
    model: GenerativeModel
    worker_models: dict[str, GenerativeModel]

    chat_session: ChatSession | None

    def __init__(self):
        # self.model = GenerativeModel(**manager_conf)
        self.worker_models = dict(
            txt2sql=GenerativeModel(**txt2sql_conf),
            interpreter=GenerativeModel(**interpreter_conf),
            facilitator=GenerativeModel(**facilitator_conf),
        )
        self.chat_session = None

    def get_process_id(self, prompt) -> dict[str, Any]:
        """
        promptから今行うべき処理のprocess_idを取得する関数
        """
        print("Debug: process特定LLMが特定開始")
        model = GenerativeModel(**organizer_conf)

        response = model.generate_content(prompt)

        ret = json.loads(response.text)

        return ret

    def facilitate(self, prompt: str) -> JSON:
        if self.chat_session is None:
            self.chat_session = self.worker_models["facilitator"].start_chat()

        response = self.chat_session.send_message(prompt, stream=False)
        return json.loads(response.text)

    def get_info(self, prompt: str) -> JSON:
        """プロンプトを元に、text-to-SQLを実行しパースされたデータを取得する"""
        query = self.run_worker_agent("txt2sql", prompt)
        dataframe_json = F.run_bq_query(query["query"])
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

    def send_message(
        self,
        prompt: str,
        strategy: JSON,
        previous_response: str,
    ) -> dict[str, Any]:
        res = self.get_process_id(
            "\n".join(
                [
                    "現在のStrategyシナリオ:",
                    json.dumps(strategy),
                    "1つ前のLLMの発言:",
                    previous_response,
                    "ユーザーの入力:",
                    prompt,
                ]
            )
        )

        process_id = res["process_id"]
        process_arg = res["arg"]

        actions = []

        if process_id == "data_question":
            prompt = "\n".join(
                [
                    prompt,
                    f"調べるべき内容: {process_arg}",
                ]
            )
            resp = self.get_info(prompt + "\n 調べるべき内容: " + process_arg)
            msg = resp["interpretation"]
            actions.append(resp)

        elif process_id == "facilitation":
            prompt = "\n".join(
                [
                    "現在のStrategyシナリオ:",
                    json.dumps(strategy),
                    f"ユーザーのinput: {prompt}",
                    f"一つ前のLLMの発言: {previous_response}",
                ]
            )
            resp = self.facilitate(prompt)
            msg = resp["msg"]
            strategy = resp["strategy_scenario"]

        elif process_id == "load_data":
            resp = dict(
                msg="(Sample) データロードが完了しました。状況が変わった時に通知します。"
            )
        else:
            resp = dict(msg="エラー: もう一度入力してください")

        return dict(msg=msg, actions=actions, strategy=strategy)

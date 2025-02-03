from vertexai.generative_models import (
    GenerativeModel,
    ChatSession,
)
from vertexai.generative_models import (
    FunctionDeclaration,
    Tool,
    ToolConfig,
)

import json
from .agent import GeminiAgent
from .models import txt2sql_conf, interpreter_conf, facilitator_conf, organizer_conf
from . import functions as F
from typing import NamedTuple


JSON: type = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


class ResponseAction(NamedTuple):
    action_type: str
    keyword_arguments: dict[str, JSON]


class ScenarioMakerResponse(NamedTuple):
    message: str
    strategy: JSON | None
    actions: list[ResponseAction]


class ScenarioMaker(GeminiAgent):
    model: GenerativeModel
    worker_models: dict[str, GenerativeModel]

    chat_session: ChatSession | None
    last_message: str

    def __init__(self, strategy: JSON):
        # self.model = GenerativeModel(**manager_conf)
        self.worker_models = dict(
            txt2sql=GenerativeModel(**txt2sql_conf),
            interpreter=GenerativeModel(**interpreter_conf),
            facilitator=GenerativeModel(**facilitator_conf),
        )
        self.chat_session = None
        self.last_message = "No previous message"
        self.strategy = strategy

        self.callable_functions = [
            FunctionDeclaration.from_func(self.get_info),
            FunctionDeclaration.from_func(self.facilitate),
            FunctionDeclaration.from_func(self.load_data),
            FunctionDeclaration.from_func(self.return_error),
        ]

    def get_process_id(self, prompt) -> tuple[str, JSON]:
        """
        promptから今行うべき処理のprocess_idを取得する関数
        """
        print("Debug: process特定LLMが特定開始")
        model = GenerativeModel(**organizer_conf)

        tool = Tool(function_declarations=self.callable_functions)
        response = model.generate_content(
            prompt,
            tools=[tool],
            tool_config=ToolConfig(
                function_calling_config=ToolConfig.FunctionCallingConfig(
                    mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
                    allowed_function_names=[],
                )
            ),
        )

        func = response.candidates[0].function_calls[0].name
        arg = response.candidates[0].function_calls[0].args

        return func, arg

    def facilitate(self, prompt: str) -> ScenarioMakerResponse:
        if self.chat_session is None:
            self.chat_session = self.worker_models["facilitator"].start_chat()

        response = self.chat_session.send_message(prompt, stream=False)
        result = json.loads(response.text)
        self.last_message = result["msg"]
        self.strategy = result["strategy_scenario"]
        return ScenarioMakerResponse(
            message=self.last_message,
            strategy=self.strategy,
            actions=[],
        )

    def load_data(self) -> ScenarioMakerResponse:
        result = ScenarioMakerResponse(
            message="(Sample) データロードが完了しました。状況が変わった時に通知します。",
            strategy=self.strategy,
            actions=[],
        )
        self.last_message = result.message
        return result

    def return_error(self) -> ScenarioMakerResponse:
        result = ScenarioMakerResponse(
            message="エラー: もう一度入力してください",
            strategy=self.strategy,
            actions=[],
        )
        return result

    def get_info(self, prompt: str) -> ScenarioMakerResponse:
        """プロンプトを元に、text-to-SQLを実行しパースされたデータを取得する"""
        query = self.run_worker_agent("txt2sql", prompt)
        dataframe_json = F.run_bq_query(query["query"])
        info = self.run_worker_agent("interpreter", dataframe_json)

        x = info["x"] if info["x"] != "NULL" else None
        y = info["y"] if info["y"] != "NULL" else None

        self.last_message = info["interpretation"]

        return ScenarioMakerResponse(
            message=self.last_message,
            strategy=self.strategy,
            actions=[
                {
                    "type": "plot",
                    "input": {
                        "source": dataframe_json,
                        "plot_type": info["plot_type"],
                        "x": x,
                        "y": y,
                    },
                }
            ],
        )

    def send_message(
        self,
        prompt: str,
    ) -> ScenarioMakerResponse:
        prompt = f"""
        現在のStrategyシナリオ:,
        {json.dumps(self.strategy)},
        1つ前のLLMの発言:,
        {self.last_message},
        ユーザーの入力:,
        {prompt},
        """
        process_id, process_arg = self.get_process_id(prompt)

        if process_id == "get_info":
            prompt = f"""
            {prompt},
            調べるべき内容:,
            {process_arg},
            """
            resp = self.get_info(prompt)

        elif process_id == "facilitate":
            prompt = f"""
            現在のStrategyシナリオ:,
            {json.dumps(self.strategy)}
            ユーザーのinput:
            {prompt}
            一つ前のLLMの発言:
            {self.last_message}
            """
            resp = self.facilitate(prompt)

        elif process_id == "load_data":
            resp = self.load_data()
        else:
            resp = self.return_error()

        return resp

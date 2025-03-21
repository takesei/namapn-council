import json
from typing import NamedTuple

from vertexai.generative_models import (
    ChatSession,
    FunctionDeclaration,
    GenerativeModel,
    Tool,
    ToolConfig,
)

from . import functions as F
from .agent import GeminiAgent
from .models import facilitator_conf, interpreter_conf, organizer_conf, txt2sql_conf

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
        self.worker_models = dict(
            txt2sql=GenerativeModel(**txt2sql_conf),
            interpreter=GenerativeModel(**interpreter_conf),
            facilitator=GenerativeModel(**facilitator_conf),
            organizer=GenerativeModel(**organizer_conf),
        )
        self.chat_session = None
        self.last_message = "No previous message"
        self.strategy = strategy

        self.callable_functions = [
            FunctionDeclaration.from_func(self.get_info),
            FunctionDeclaration.from_func(self.facilitate),
            FunctionDeclaration.from_func(self.register_strategy_scenario),
        ]

    def get_process_id(self, prompt) -> tuple[str, JSON]:
        """
        promptから今行うべき処理のprocess_idを取得する関数
        """
        print("Debug: process特定LLMが特定開始")
        tool = Tool(function_declarations=self.callable_functions)
        response = self.worker_models["organizer"].generate_content(
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
        """
        任意のタイミングで実行ができる, 会議の司会進行を担う関数.
        ユーザーとの対話を元にMTGのファシリテーションを行う場合、基本的にはこれを選択する。

        Args:
            prompt: str ユーザからの質問やコメント, 提案

        Returns: ScenarioMakerResponse
            ScenarioMakerResponse.msg: 司会進行に伴うメッセージ
            ScenarioMakerResponse.strategy: 最新の対策シナリオ
            ScenarioMakerResponse.actions: 空の配列
        """
        if self.chat_session is None:
            self.chat_session = self.worker_models["facilitator"].start_chat()

        print("===FACILITATION===")
        response = self.chat_session.send_message(prompt, stream=False)
        result = json.loads(response.text)
        self.last_message = "  \n".join(
            [
                f"Agenda: **{result['current_topic']}**",
                f"ステップ: **{result['current_step']}**"
                if result["current_step"] != ""
                else "",
                result["msg"],
            ]
        )
        print("== message")
        print(self.last_message)

        print("== Chaning point of Strategy Scenario")
        print(result["strategy_scenario"])
        self._update_strategy_scenario(result["strategy_scenario"])
        print("== modified scenario")
        print(result["strategy_scenario"])
        print("===DONE===")
        return ScenarioMakerResponse(
            message=self.last_message,
            strategy=self.strategy,
            actions=[],
        )

    def _update_strategy_scenario(self, diff_scneario: list[JSON]) -> None:
        for value in diff_scneario:
            name = value["name"]
            cont = value["content"]

            name_list = name.split(".")
            field = name_list[0]
            subfiled = name_list[1:-1]
            attr = name_list[-1]

            if field == attr:
                self.strategy[field] = cont
            elif len(subfiled) == 0:
                self.strategy[field][attr] = cont
            else:
                temp = self.strategy[field]
                for sf in subfiled:
                    if sf not in temp:
                        temp[sf] = {}
                    temp = temp[sf]
                temp[attr] = cont

    def register_strategy_scenario(self) -> ScenarioMakerResponse:
        """
        Agenda: [対策シナリオの登録] のタイミングで実行する.
        特に, データの読み込みを行う指示をユーザーから受けた場合に選択する
        対策シナリオの結果を保存し, 全体に共有をする.

        Args:
            None

        Returns: ScenarioMakerResponse
            ScenarioMakerResponse.msg: 対策シナリオの成功の可否と, 保存された先のurl
            ScenarioMakerResponse.strategy: 保存した対策シナリオ
            ScenarioMakerResponse.actions: 空の配列
        """
        print("===DATALOAD(DUMMY)===")
        result = ScenarioMakerResponse(
            message="(Sample) データロードが完了しました。状況が変わった時に通知します。",
            strategy=self.strategy,
            actions=[],
        )
        self.last_message = result.message
        print("===DONE===")
        return result

    def get_info(self, prompt: str) -> ScenarioMakerResponse:
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
        print("===RUN TXT2BQ===")
        query = self.run_worker_agent("txt2sql", prompt)
        dataframe_json = F.run_bq_query(query["query"])
        info = self.run_worker_agent(
            "interpreter", f"dataframe: {dataframe_json}\nprompt: {prompt}"
        )

        x = info["x"] if info["x"] != "NULL" else None
        y = info["y"] if info["y"] != "NULL" else None

        self.last_message = info["interpretation"]

        print("===DONE===")
        return ScenarioMakerResponse(
            message=self.last_message,
            strategy=self.strategy,
            actions=[
                ResponseAction(
                    "plot",
                    dict(source=dataframe_json, plot_type=info["plot_type"], x=x, y=y),
                )
            ],
        )

    def _generate_prompt(self, user_input: str) -> str:
        return f"""
        現在のStrategyシナリオ: {json.dumps(self.strategy, indent=2)}
        1つ前のLLMの発言: {self.last_message}
        ユーザーの入力: {user_input}
        """

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

        elif process_id == "register_strategy_scenario":
            resp = self.register_strategy_scenario()
        else:
            resp = self.facilitate(prompt)

        return resp

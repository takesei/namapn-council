from vertexai.generative_models import (
    FunctionDeclaration,
    GenerativeModel,
)

from libs.typing import EventScenario, ProcessCaller, StrategyScenario
from libs.typing import JSON

from libs.genai.agent import AgentResponse
from libs.genai.strategy_agent.facilitator import FacilitatorAgent
from libs.genai.strategy_agent.insight import InsightAgent
from libs.genai.strategy_agent.organizer import OrganizerAgent


class StrategyAgent:
    models: dict[str, GenerativeModel]
    strategy: StrategyScenario
    event: EventScenario

    last_message: str

    def __init__(self):
        self.models = dict(
            facilitator=FacilitatorAgent(),
            insight=InsightAgent(),
            organizer=OrganizerAgent(),
        )
        fn_f = FunctionDeclaration.from_func(self.models["facilitator"].send_message)
        fn_i = FunctionDeclaration.from_func(self.models["insight"].send_message)
        fn_f._raw_function_declaration.name = "facilitator_send_message"
        fn_i._raw_function_declaration.name = "insight_send_message"

        self.models["organizer"].function_declarations = [
            # fn_f,
            fn_i,
            # FunctionDeclaration.from_func(self.register_strategy_scenario),
        ]
        self.strategy = StrategyScenario()
        self.last_message = "No previous message"

    def send_worker_message[U](self, model_name: str, prompt: str) -> AgentResponse[U]:
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        agent = self.models[model_name]
        return agent.send_message(prompt)

    def send_message(
        self,
        prompt: str,
    ) -> AgentResponse[ProcessCaller | StrategyScenario | None]:
        prompt = f"""
        現在のStrategyシナリオ:,
        {self.strategy.to_dict()},
        1つ前のLLMの発言:,
        {self.last_message},
        ユーザーの入力:,
        {prompt},
        """

        print("\n========== Gererate Content ==========")
        _, attachments = self.send_worker_message("organizer", prompt)

        name = attachments.name
        kwargs = attachments.kwargs

        if name == "insight_send_message":
            prompt = f"""
            {prompt},
            調べるべき内容:,
            {kwargs},
            """
            resp = self.send_worker_message("insight", prompt)

        elif name == "register_strategy_scenario":
            resp = self.register_strategy_scenario()
            self.strategy_scenario = self._update_strategy_scenario(resp.attachments)
        elif name == "facilitator_send_message":
            resp = self.send_worker_message("facilitator", prompt)
        else:
            print(f">>> organizer order not hit, {name}, {kwargs} <<<")
            resp = self.send_worker_message("facilitator", prompt)

        print("== message")
        self.last_message = resp.message
        print(self.last_message)

        print("========== Finish Content ==========\n")

        return resp

    def register_strategy_scenario(self) -> AgentResponse[None]:
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
        result = AgentResponse(
            message="(Sample) データロードが完了しました。状況が変わった時に通知します。",
            attachments=None,
        )
        self.last_message = result.message
        print("===DONE===")
        return result

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

    def _generate_prompt(self, user_input: str) -> str:
        return f"""
        現在のStrategyシナリオ: {self.strategy.to_dict()}
        1つ前のLLMの発言: {self.last_message}
        ユーザーの入力: {user_input}
        """

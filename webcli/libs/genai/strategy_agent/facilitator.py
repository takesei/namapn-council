import json

from vertexai.generative_models import (
    ChatSession,
    GenerativeModel,
)

from libs.typing import StrategyScenario

from libs.genai.agent import AgentResponse
from libs.genai.loader import load_config_as_gemini_agent


class FacilitatorAgent:
    model: GenerativeModel
    chat_session: ChatSession | None

    def __init__(self) -> None:
        self.chat_session = None
        self.model = load_config_as_gemini_agent(
            "libs.genai.strategy_agent.config.facilitator"
        )

    def send_message(self, prompt: str) -> AgentResponse[StrategyScenario]:
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
            self.chat_session = self.model.start_chat()

        print("===FACILITATION===")
        response = self.chat_session.send_message(prompt, stream=False)
        result = json.loads(response.text)
        message = "  \n".join(
            [
                f"Agenda: **{result['current_topic']}**",
                f"ステップ: **{result['current_step']}**"
                if result["current_step"] != ""
                else "",
                result["msg"],
            ]
        )
        print("== Chaning point of Strategy Scenario")
        print(result["strategy_scenario"])
        print("===DONE===")
        return AgentResponse(
            message=message,
            attachments=result["strategy_scenario"],
        )

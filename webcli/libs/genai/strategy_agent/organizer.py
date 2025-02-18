from vertexai.generative_models import (
    GenerativeModel,
    Tool,
    ToolConfig,
    FunctionDeclaration,
)

from libs.typing import ProcessCaller

from libs.genai.agent import AgentResponse
from libs.genai.loader import load_config_as_gemini_agent


class OrganizerAgent:
    model: GenerativeModel
    function_declarations: FunctionDeclaration | None

    def __init__(self, function_declarations: FunctionDeclaration | None = None):
        self.model = load_config_as_gemini_agent(
            "libs.genai.strategy_agent.config.organizer"
        )
        self.function_declarations = function_declarations

    def send_message(self, prompt: str) -> AgentResponse[ProcessCaller]:
        """
        promptから今行うべき処理のprocess_idを取得する関数
        """
        if self.function_declarations is None:
            raise ValueError("Functions isn't declarated yet'")
        print("===Organizer===")
        tool = Tool(function_declarations=self.function_declarations)
        response = self.model.generate_content(
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
        print("== Called Function")
        print(func, arg)
        print("===DONE===")
        return AgentResponse(
            message=None, attachments=ProcessCaller(name=func, kwargs=arg)
        )

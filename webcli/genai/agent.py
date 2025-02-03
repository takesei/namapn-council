from typing import Any, Generator
import json
from vertexai.generative_models import (
    GenerativeModel,
    ChatSession,
)


class GeminiAgent:
    model: GenerativeModel
    worker_models: dict[str, GenerativeModel]

    chat_session: ChatSession | None

    def run_worker_agent(self, worker_name: str, prompt: str) -> dict[str, Any]:
        model = self.worker_models[worker_name]
        content = model.generate_content(prompt, stream=False).text

        return json.loads(content)

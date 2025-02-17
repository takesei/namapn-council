from typing import NamedTuple, Protocol, Any


class AgentResponse[T](NamedTuple):
    message: str | None
    attachments: T


class Agent[T](Protocol):
    def send_message(prompt: str) -> AgentResponse[T]: ...


class MultiAgent[T]:
    models: dict[str, Agent[Any]]

    def send_worker_message[U](self, model_name: str, prompt: str) -> AgentResponse[U]:
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        agent = self.models[model_name]
        return agent.send_message(prompt)

from typing import Any, NamedTuple

import streamlit as st

from .actions import run_action
from libs.genai import AgentResponse

from typing import Protocol


class Message(NamedTuple):
    actor: str
    message: str
    attachments: list[Any]


class AgentModel[T](Protocol):
    def send_message(prompt: str) -> AgentResponse[T]: ...


# Main UI
def render_agent_interface(chat_history: list[Message]):
    st.subheader(":material/support_agent: Planning Companion", divider="grey")
    chat_history_container = st.container(border=True, height=640)
    prompt_container = st.container()

    with chat_history_container:
        render_chat_history(chat_history)

    with prompt_container:
        render_prompt_area(chat_history_container, chat_history)


# Sub UI
def send_agent_prompt(model: AgentModel, prompt: str) -> Message:
    resp: AgentResponse = model.send_message(prompt)
    cont = Message(
        actor="assistant",
        message=resp.message,
        attachments=resp.actions,
    )
    return cont


def render_chat_history(chat_history: list[Message]) -> None:
    for msg in chat_history:
        with st.chat_message(msg.actor):
            msg.message  # magic cmd
            for a in msg.attachments:
                run_action(a)


def render_prompt_area(chat_history_container: "st.container", chat_history) -> None:
    if prompt := st.chat_input("What is up?"):
        chat_history.append(Message(actor="user", message=prompt, attachments=[]))

        with chat_history_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    resp = st.session_state.agent["model"].send_message(prompt)
                    st.write(resp.message)
                    run_action(resp.actions)
                    cont = Message(
                        actor="assistant",
                        message=resp.message,
                        attachments=resp.actions,
                    )
                except Exception as e:
                    st.error(e)
                    cont = Message(
                        actor="assistant",
                        message=f"error: {e}",
                        attachments=[],
                    )
            chat_history.append(cont)

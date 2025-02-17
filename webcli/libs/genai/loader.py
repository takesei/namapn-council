import yaml
import json
from importlib import resources

from vertexai.generative_models import (
    GenerativeModel,
    GenerationConfig,
    Part,
    SafetySetting,
    HarmCategory,
    HarmBlockThreshold
)


def load_config_as_gemini_agent(config_location: str) -> GenerativeModel:
    location = resources.files(config_location)
    with location.joinpath("config.yml").open("r", encoding="utf-8") as f:
        _config = yaml.safe_load(f)

    si = ""

    if "system_instruction" in _config:
        src = _config["system_instruction"]["src"]
        with location.joinpath(src).open("r", encoding="utf-8") as f:
            si += f.read()
        if "attachments" in _config:
            for att in _config["system_instruction"]["attachments"]:
                label = att["label"]
                with location.joinpath(att["src"]).open("r", encoding="utf-8") as f:
                    att_cont = f.read()
                si += f"\n--- [{label}]\n{att_cont}"

    if "prompt_prefix" in _config:
        si += _config["prompt_prefix"]

    generation_config = {}
    if "generation_config" in _config:
        generation_config |= _config["generation_config"]

    if "response" in _config:
        with location.joinpath(_config["response"]["schema_src"]).open(
            "r", encoding="utf-8"
        ) as f:
            schema = json.load(f)

        generation_config |= {
            "response_schema": schema,
            "response_mime_type": _config["response"]["mime_type"],
            "response_modalities": _config["response"]["modalities"],
        }

    safety_settings = []
    if "safety_config" in _config:
        for sc in _config["safety_config"]:
            safety_settings.append(
                SafetySetting(
                    category=HarmCategory[sc["category"]],
                    threshold = HarmBlockThreshold[sc["threshold"]]
                )
            )

    config = dict(
        model_name=_config["model_name"],
        system_instruction=Part.from_text(si),
        generation_config=GenerationConfig(**generation_config),
        safety_settings=safety_settings,
    )

    return GenerativeModel(**config)

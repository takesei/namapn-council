from vertexai.generative_models import (
    GenerationConfig,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    SafetySetting,
)

system_instruction = """
あなたはMTGに参加しています.
ユーザから送られるプロンプトを, どの関数に送るべきかを考えてください.
与えられたpromptを元にして、適切なprocess_idを1つ選択してください。
prompt: """

response_schema = {
    "type": "object",
    "properties": {
        "process_id": {"type": "string"},
        "process_arg": {"type": "string"},
    },
    "required": ["process_id", "process_arg"],
}

safety_config = [
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=HarmBlockThreshold.BLOCK_NONE,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.BLOCK_NONE,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.BLOCK_NONE,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=HarmBlockThreshold.BLOCK_NONE,
    ),
]

organizer_conf = dict(
    model_name="gemini-1.5-flash",
    safety_settings=safety_config,
    generation_config=GenerationConfig(
        temperature=0,
        top_p=0.95,
    ),
    system_instruction=[Part.from_text(system_instruction)],
)

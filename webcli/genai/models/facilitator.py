from vertexai.generative_models import GenerationConfig, Part
import json

with open("genai/models/prompts/facilitator.md", "r") as f:
    base_instruction = f.read()

with open("templates/schema_event.json") as f:
    schema_event = json.load(f)
with open("templates/schema_strategy.json") as f:
    schema_strategy = json.load(f)

with open("templates/workflow_strategy.md") as f:
    workflow_strategy = f.read()

system_instruction = f"""
{base_instruction}

--- [イベントシナリオスキーマ]
{schema_event}
--- [対策シナリオスキーマ]
{schema_strategy}
--- [ステップ] と [変数の設定方法]
{workflow_strategy}

Data: """

response_schema = {
    "type": "object",
    "properties": {
        "msg": {
            "type": "string",
            "description": "LLMからUserへのメッセージをマークダウン形式で記載する",
        },
        "strategy_scenario": {
            "title": "イベント対応対策シナリオ",
            "description": "Agendaが[対策シナリオの作成]でかつ, 対策シナリオの内容を変更する場合に記載する. 対策シナリオの変更点に関する情報を記述する",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "title": "対策シナリオスキームの変数名",
                        "description": "対策シナリオで変更する変数の名を記載する",
                    },
                    "content": {
                        "type": "string",
                        "title": "対策シナリオスキームの変数の値",
                        "description": "対策シナリオで変更する変数の値を記載する, 必ずjsonのスキーマの型に沿って設定をすること",
                    },
                },
                "required": ["name", "content"],
            },
        },
        "current_topic": {
            "type": "string",
            "description": "現在のAgendaの順序を記載する",
        },
        "current_step": {
            "type": "string",
            "description": "Agendaが[対策シナリオの作成]の場合は, ここに現在のステップを記載する",
        },
    },
    "required": ["msg", "strategy_scenario", "current_topic", "current_step"],
}

facilitator_conf = dict(
    model_name="gemini-2.0-flash-exp",
    generation_config=GenerationConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_modalities=["TEXT"],
        response_schema=response_schema,
    ),
    system_instruction=[Part.from_text(system_instruction)],
)

from vertexai.generative_models import GenerationConfig, Part

system_instruction = """
You are a process selector. You have the role of giving instructions to other LLMs.
与えられたpromptを元にして、適切なprocess_idを1つ選択してください。

下記のような状況を想定します。
あなたはmaker (company) の社内システムです。makerはsupplierから原材料の調達を受けています。makerはretailerに商品を販売しています。
makerでは飲料を製造しています。
社内のSupplier Chain Managementを補佐するために業務を行ってください。

process_idは下記のいずれかから選択してください。
- "data_question"
  - ユーザーからデータに関する質問を受けた場合に選択する。
  - データを調べる必要があるようなものがあったときにはこれを適用する。
  - argには調べるべきデータの内容を日本語で詳細に記載してください。
- "load_data"
  - データの読み込みを行う指示をユーザーから受けた場合に選択する
  - argにはスプレッドシートデータのurlのみを出力してください。
- "facilitation"
  - ユーザーとの対話を元にMTGのファシリテーションを行う場合、基本的にはこれを選択する。
  - argには"ファシリテーションをしてください"と出力。
- "insufficient_info": 
  - ユーザーから提供された情報が不十分な場合に選択する。
  - 不足している情報として何が必要かをargに記載してください。

prompt: """

response_schema = {
    "type": "object",
    "properties": {
        "process_id": {"type": "string"},
        "process_arg": {"type": "string"},
    },
    "required": ["process_id", "process_arg"],
}

organizer_conf = dict(
    model_name="gemini-1.5-flash",
    generation_config=GenerationConfig(
        temperature=1,
        top_p=0.95,
    ),
    system_instruction=[Part.from_text(system_instruction)],
)

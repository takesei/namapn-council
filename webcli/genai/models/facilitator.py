from vertexai.generative_models import GenerationConfig, Part

system_instruction = """
あなたはMTGの会議の進行を行うファシリテーションの専門家です.
MTGでは以下の「MTG情報」を穴埋めすることを目的としており, 皆が適切に全ての穴を埋められるようにあなたは情報を整理したり, 議論を誘導する必要があります. 穴埋めの結果は最終的に, 「MTGテンプレート」に埋め込まれて出力をされます.

穴埋めの項目には, (自動):自動で埋まるもの, (半自動):自動で決まるものの意思決定も必要なもの, (手動):意思決定なしには埋められないもの, の3つがあり, また, ある項目を決めるには別の項目を決めないと決められないと言ったような, それぞれに決める順番があるはずです. その情報は, 「MTGの進め方」に記載しました. この情報を元に, 情報を一つずつあなたは埋めていくお手伝いをしていってください.

また, しばしば, 穴埋めをするための情報を集めるために, 一見関係のない議論をするケースもあります.
その時は脱線しすぎない程度に場を収めてください.

inputとして, あなたは質問や議論, 決定したい情報などの幅広い内容の話を投げかけられます.
outputとして, inputに対してあなたは, それが果たして穴埋めに関係があるのか, その内容で穴埋めするのに十分かを明示した上で質問に答えてください.
もし, 穴埋めするのに情報が十分でないならば何が足りないかを教えてあげてください.
また, 同時にoutputとしては, 次に何の情報を埋めるべきか, そしてそれをするためには何が必要かのおすすめの情報も出してあげてください.

--- MTG情報
{"properties":{"scenario_name":{"type":"string","description":"シナリオの名称(例:'関西シナリオ（調達影響）')"},"scenario_id":{"type":"string","description":"ユニークなシナリオ識別子(例:'20250914_Kansai_Supply')"},"conditions":{"type":"string","description":"シナリオが適用される条件(例:'台風が関西圏に直撃し、物流・調達に影響を及ぼす場合')"},"severity":{"type":"string","enum":["中度","重大"],"description":"シナリオの深刻度（選択式:'中度'または'重大'）"},"objectives":{"type":"array","description":"シナリオの目的をリストで記述(例:['調達計画の影響最小化','関係者への迅速な通知と調整'])","items":{"type":"string"}},"activation":{"type":"object","description":"シナリオ発動条件と責任者","properties":{"responsible":{"type":"string","description":"発動の責任者(例:'危機管理部門')"},"criteria":{"type":"string","description":"シナリオが発動される基準(例:'09/13深夜の気象庁最終発表で関西直撃が確定')"},"notifications":{"type":"array","description":"通知を行う対象部門(例:['調達部門','物流部門','生産管理部門'])","items":{"type":"string"}}},"required":["responsible","criteria","notifications"]},"initial_response":{"type":"array","description":"初動対応のアクションリスト(0〜30分内の対応)","items":{"type":"object","properties":{"name":{"type":"string","description":"アクションの名称(例:'倉庫の在庫確認')"},"responsible":{"type":"string","description":"担当部署(例:'調達部門')"},"details":{"type":"string","description":"対応の具体的な内容(例:'関西倉庫の在庫を緊急チェックし、影響範囲を特定')"}},"required":["name","responsible","details"]}},"containment_measures":{"type":"array","description":"封じ込め・一時対策(30分〜数時間内の対応)","items":{"type":"object","properties":{"name":{"type":"string","description":"アクションの名称(例:'サプライヤーとの調達交渉')"},"responsible":{"type":"string","description":"担当部署(例:'危機管理部門')"},"details":{"type":"string","description":"対応の具体的な内容(例:'追加調達')"}},"required":["name","responsible","details"]}},"monitoring":{"type":"array","description":"継続的な監視・モニタリング対応(数時間〜収束まで)","items":{"type":"object","properties":{"name":{"type":"string","description":"アクションの名称(例:'調達・物流状況の監視')"},"responsible":{"type":"string","description":"担当部署(例:'調達部門')"},"details":{"type":"string","description":"対応の具体的な内容(例:'物流回復までの在庫管理を継続')"}},"required":["name","responsible","details"]}},"recovery":{"type":"array","description":"復旧プロセス・フォローアップ","items":{"type":"object","properties":{"name":{"type":"string","description":"アクションの名称(例:'通常調達プロセスへの移行')"},"responsible":{"type":"string","description":"担当部署(例:'調達部門')"},"details":{"type":"string","description":"対応の具体的な内容(例:'物流回復後、通常の調達へ戻す')"}},"required":["name","responsible","details"]}},"risks_and_alternatives":{"type":"array","description":"リスク評価と代替シナリオへの切り替え","items":{"type":"object","properties":{"scenario":{"type":"string","description":"リスクのシナリオ(例:'関東・九州からの調達が困難な場合')"},"details":{"type":"string","description":"対応策(例:'他国からの輸入や別サプライヤーを検討')"}},"required":["scenario","details"]}},"communication_plan":{"type":"array","description":"影響範囲への通知計画","items":{"type":"object","properties":{"target":{"type":"string","description":"通知対象(例:'社内通知')"},"responsible":{"type":"string","description":"通知を担当する部門(例:'危機管理部門')"},"details":{"type":"string","description":"通知内容(例:'全体メールおよび緊急会議を開催')"}},"required":["target","responsible","details"]}},"related_incident":{"type":"string","description":"関連するインシデントシナリオ(例:'2025/09/14台風直撃インシデント')"},"additional_references":{"type":"array","description":"関連リンク・詳細資料","items":{"type":"object","properties":{"name":{"type":"string","description":"資料名(例:'過去事例')"},"link":{"type":"string","description":"参照リンク(例:'2023年台風12号の影響分析')"}},"required":["name","link"]}}},"required":["scenario_name","scenario_id","conditions","severity","activation","related_incident"]}

--- MTGテンプレート
{% raw %}
# 📌 ダメコンシナリオ: {{ scenario_name }}

## 1. シナリオ名 / ID / 適用条件
- **シナリオ名:** {{ scenario_name }}
- **ID:** {{ scenario_id }}
- **適用条件:** {{ conditions }}
- **深刻度:** {{ severity }}

## 2. 目的
{% if objectives %}
 {% for objective in objectives %}
20
facilitatror_conffacilitator_conf
{% endif %}

## 3. 手順・フロー

### (1) アクティベーション（発動）
- **責任者:** {{ activation.responsible }}
- **判断基準:** {{ activation.criteria }}
- **通知:** {{ activation.notifications | join(", ") }}

### (2) 初動対応 (0〜30分)
{% if initial_response %}
 {% for action in initial_response %}
- **{{ action.name }}**  
 - **担当:** {{ action.responsible }}  
 - **実施期限:** {{ action.deadline }}  
 - **内容:** {{ action.details }}
 {% endfor %}
{% endif %}

### (3) 封じ込め・一時対策 (30分〜数時間)
{% if containment_measures %}
 {% for action in containment_measures %}
- **{{ action.name }}**  
 - **担当:** {{ action.responsible }}  
 - **実施期限:** {{ action.deadline }}  
 - **内容:** {{ action.details }}
 {% endfor %}
{% endif %}

### (4) 維持・モニタリング (数時間〜収束まで)
{% if monitoring %}
 {% for action in monitoring %}
- **{{ action.name }}**  
 - **担当:** {{ action.responsible }}  
 - **実施期限:** {{ action.deadline }}  
 - **内容:** {{ action.details }}
 {% endfor %}
{% endif %}

### (5) 復旧プロセス・フォローアップ
{% if recovery %}
 {% for action in recovery %}
- **{{ action.name }}**  
 - **担当:** {{ action.responsible }}  
 - **実施期限:** {{ action.deadline }}  
 - **内容:** {{ action.details }}
 {% endfor %}
{% endif %}

## 4. 必要リソース
- **人員:** {{ resources.staff | join(", ") }}
- **装備:** {{ resources.equipment | join(", ") }}
- **予算:** {{ resources.budget }}

## 5. リスクと分岐（他シナリオへの切り替え）
{% if risks_and_alternatives %}
 {% for risk in risks_and_alternatives %}
- **{{ risk.scenario }}:** {{ risk.details }}
 {% endfor %}
{% endif %}

## 6. コミュニケーション計画
{% if communication_plan %}
 {% for plan in communication_plan %}
- **{{ plan.target }}:**  
 - **担当:** {{ plan.responsible }}  
 - **内容:** {{ plan.details }}
 {% endfor %}
{% endif %}

## 7. 関連リンク・詳細資料
- **インシデントシナリオ:** {{ related_incident }}
{% if additional_references %}
 {% for reference in additional_references %}
- **{{ reference.name }}:** {{ reference.link }}
 {% endfor %}
{% endif %}
{% endraw %}

--- MTGの進め方
| ステップ | 作業内容 | 説明 | 自動化の度合い | 変数名 | 必要な前提情報 |
|------------|-------------------------|------------------------------------------------|------------|-----------------------------|---------------------------|
| 1 | シナリオ名 / ID / 適用条件を確定 | インシデントシナリオから自動取得し、IDを生成 | ✅ 自動 | `scenario_name` / `scenario_id` / `conditions` | なし |
| 2 | 発動条件の責任者・基準を決定 | 発動条件（台風直撃など）をインシデント情報から取得 | ✅ 自動 | `activation.responsible` / `activation.criteria` | `scenario_name` / `scenario_id` / `conditions` |
| 3 | 関連インシデントシナリオを記入 | 過去の事例や関連するインシデントをリスト化 | ✅ 自動 | `related_incident` | `scenario_name` / `scenario_id` |
| 4 | 追加の参考資料を取得 | インシデントシナリオや過去事例を自動検索し取得 | ✅ 自動 | `additional_references` | `related_incident` |
| 5 | 深刻度を決定 | 影響範囲をもとに自動提案されるが、最終確定は手動 | 🔹 半自動 | `severity` | `scenario_name` / `conditions` |
| 6 | 通知対象を決定 | 影響範囲をもとに自動提案されるが、調整が必要 | 🔹 半自動 | `activation.notifications` | `scenario_name` / `severity` |
| 7 | シナリオの目的を定義 | 何を守るためのシナリオか、目的を明確化 | ❌ 手動 | `objectives` | `scenario_name` / `severity` / `conditions` |
| 8 | 初動対応の手順を決定 | 過去の標準対応をベースに自動提案、関係者と調整 | 🔹 半自動 | `initial_response` | `objectives` / `severity` |
| 9 | 封じ込め・一時対策を決定 | 影響度に応じた対策を自動提案、関係者と調整 | 🔹 半自動 | `containment_measures` | `objectives` / `severity` / `initial_response` |
| 10 | 維持・モニタリングの計画を策定 | 標準監視手順を提案し、適用範囲を調整 | 🔹 半自動 | `monitoring` | `objectives` / `severity` / `containment_measures` |
| 11 | 復旧プロセスを決定 | 過去の復旧手順を参考に関係者と調整 | 🔹 半自動 | `recovery` | `objectives` / `severity` / `monitoring` |
| 12 | 必要リソースを決定 | 過去の事例から自動提案されるが、調整が必要 | 🔹 半自動 | `resources` | `initial_response` / `containment_measures` / `monitoring` / `recovery` |
| 13 | リスクと代替シナリオを検討 | 影響に応じてリスクシナリオを分析 | ❌ 手動 | `risks_and_alternatives` | `severity` / `containment_measures` / `monitoring` |
| 14 | 通知計画を策定 | 影響範囲と通知内容を整理 | ❌ 手動 | `communication_plan` | `initial_response` / `containment_measures` / `monitoring` / `risks_and_alternatives` |
| 15 | 通知内容の詳細を決定 | 各通知のメッセージを作成 | ❌ 手動 | `communication_plan[].details` | `communication_plan` |
| 16 | 担当者と実施期限を割り当て | 各対応の責任者と期限を決定 | ❌ 手動 | `initial_response[].responsible` / `containment_measures[].responsible` / `monitoring[].responsible` / `recovery[].responsible` | `initial_response` / `containment_measures` / `monitoring` / `recovery` |
Data: """
response_schema = {
    "type": "object",
    "properties": {
        "msg": {
            "type": "string",
            "description": "LLMからUserへのメッセージをマークダウン形式で記載する",
        },
        "strategy_scenario": {
            "title": "戦略シナリオデータ",
            "description": "戦略シナリオの標準フォーマット",
            "type": "object",
            "properties": {
                "scenario_name": {
                    "type": "string",
                    "description": "シナリオの名称(例:'関西シナリオ（調達影響）')",
                },
                "scenario_id": {
                    "type": "string",
                    "description": "ユニークなシナリオ識別子(例:'20250914_Kansai_Supply')",
                },
                "conditions": {
                    "type": "string",
                    "description": "シナリオが適用される条件(例:'台風が関西圏に直撃し、物流・調達に影響を及ぼす場合')",
                },
                "severity": {
                    "type": "string",
                    "enum": ["中度", "重大"],
                    "description": "シナリオの深刻度（選択式:'中度'または'重大'）",
                },
                "objectives": {
                    "type": "array",
                    "description": "シナリオの目的をリストで記述(例:['調達計画の影響最小化','関係者への迅速な通知と調整'])",
                    "items": {"type": "string"},
                },
                "activation": {
                    "type": "object",
                    "description": "シナリオ発動条件と責任者",
                    "properties": {
                        "responsible": {
                            "type": "string",
                            "description": "発動の責任者(例:'危機管理部門')",
                        },
                        "criteria": {
                            "type": "string",
                            "description": "シナリオが発動される基準(例:'09/13深夜の気象庁最終発表で関西直撃が確定')",
                        },
                        "notifications": {
                            "type": "array",
                            "description": "通知を行う対象部門(例:['調達部門','物流部門','生産管理部門'])",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["responsible", "criteria", "notifications"],
                },
                "initial_response": {
                    "type": "array",
                    "description": "初動対応のアクションリスト(0〜30分内の対応)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "アクションの名称(例:'倉庫の在庫確認')",
                            },
                            "responsible": {
                                "type": "string",
                                "description": "担当部署(例:'調達部門')",
                            },
                            "details": {
                                "type": "string",
                                "description": "対応の具体的な内容(例:'関西倉庫の在庫を緊急チェックし、影響範囲を特定')",
                            },
                        },
                        "required": ["name", "responsible", "details"],
                    },
                },
                "containment_measures": {
                    "type": "array",
                    "description": "封じ込め・一時対策(30分〜数時間内の対応)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "アクションの名称(例:'サプライヤーとの調達交渉')",
                            },
                            "responsible": {
                                "type": "string",
                                "description": "担当部署(例:'危機管理部門')",
                            },
                            "details": {
                                "type": "string",
                                "description": "対応の具体的な内容(例:'追加調達')",
                            },
                        },
                        "required": ["name", "responsible", "details"],
                    },
                },
                "monitoring": {
                    "type": "array",
                    "description": "継続的な監視・モニタリング対応(数時間〜収束まで)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "アクションの名称(例:'調達・物流状況の監視')",
                            },
                            "responsible": {
                                "type": "string",
                                "description": "担当部署(例:'調達部門')",
                            },
                            "details": {
                                "type": "string",
                                "description": "対応の具体的な内容(例:'物流回復までの在庫管理を継続')",
                            },
                        },
                        "required": ["name", "responsible", "details"],
                    },
                },
                "recovery": {
                    "type": "array",
                    "description": "復旧プロセス・フォローアップ",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "アクションの名称(例:'通常調達プロセスへの移行')",
                            },
                            "responsible": {
                                "type": "string",
                                "description": "担当部署(例:'調達部門')",
                            },
                            "details": {
                                "type": "string",
                                "description": "対応の具体的な内容(例:'物流回復後、通常の調達へ戻す')",
                            },
                        },
                        "required": ["name", "responsible", "details"],
                    },
                },
                "risks_and_alternatives": {
                    "type": "array",
                    "description": "リスク評価と代替シナリオへの切り替え",
                    "items": {
                        "type": "object",
                        "properties": {
                            "scenario": {
                                "type": "string",
                                "description": "リスクのシナリオ(例:'関東・九州からの調達が困難な場合')",
                            },
                            "details": {
                                "type": "string",
                                "description": "対応策(例:'他国からの輸入や別サプライヤーを検討')",
                            },
                        },
                        "required": ["scenario", "details"],
                    },
                },
                "communication_plan": {
                    "type": "array",
                    "description": "影響範囲への通知計画",
                    "items": {
                        "type": "object",
                        "properties": {
                            "target": {
                                "type": "string",
                                "description": "通知対象(例:'社内通知')",
                            },
                            "responsible": {
                                "type": "string",
                                "description": "通知を担当する部門(例:'危機管理部門')",
                            },
                            "details": {
                                "type": "string",
                                "description": "通知内容(例:'全体メールおよび緊急会議を開催')",
                            },
                        },
                        "required": ["target", "responsible", "details"],
                    },
                },
                "related_incident": {
                    "type": "string",
                    "description": "関連するインシデントシナリオ(例:'2025/09/14台風直撃インシデント')",
                },
                "additional_references": {
                    "type": "array",
                    "description": "関連リンク・詳細資料",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "資料名(例:'過去事例')",
                            },
                            "link": {
                                "type": "string",
                                "description": "参照リンク(例:'2023年台風12号の影響分析')",
                            },
                        },
                        "required": ["name", "link"],
                    },
                },
            },
            "required": [
                "scenario_name",
                "scenario_id",
                "conditions",
                "severity",
                "activation",
                "related_incident",
            ],
        },
    },
    "required": ["msg", "strategy_scenario"],
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

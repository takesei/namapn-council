from vertexai.generative_models import GenerationConfig, Part

system_instruction = """
あなたはMTGの会議の進行を行うファシリテーションの専門家です.
MTGでは以下の「対策シナリオ」を穴埋めすることを目的としており, 皆が適切に全ての穴を埋められるようにあなたは情報を整理したり, 議論を誘導する必要があります. 

穴埋めの項目には, (自動):自動で埋まるもの, (半自動):自動で決まるものの意思決定も必要なもの, (手動):意思決定なしには埋められないもの, の3つがあり, また, ある項目を決めるには別の項目を決めないと決められないと言ったような, それぞれに決める順番があるはずです. その情報は, 「MTGの進め方」に記載しました. この情報を元に, 情報を一つずつあなたは埋めていくお手伝いをしていってください.

MTGはステップごとに進めます. ステップに入ったら, 変数を埋める順番に則り, 一つずつ変数を考案します.
変数を埋める際には必ずユーザに確認をし, 一つずつ許可をとってください.
ステップで設定するべきすべての変数を埋め終わったら, ステップが終了したことをユーザに通知し, 次のステップに言ってください.
ユーザはわがままです, 時に前に設定した変数を戻したい, という話をするかと思います. その場合は現状の変数を埋めている順番を記憶して, 一時的に前に戻ってください.
ステップを前に戻す場合も同様です. 具体的にステップの中にあるどの変数を戻したいかを確認し, 現状の変数を埋めている順番を記憶して, 一時的に前に戻ってください.
前に戻った時の変数を埋め終わったらば, そのまま記憶した順番を元に, 進行を戻しましょう.

しばしば, 穴埋めをするための情報を集めるために, 一見関係のない議論をするケースもあります.
その時は脱線しすぎない程度に場を収めてください.

inputとして, あなたは質問や議論, 決定したい情報などの幅広い内容の話を投げかけられます.
outputとして, inputに対してあなたは, それが果たして穴埋めに関係があるのか, その内容で穴埋めするのに十分かを明示した上で質問に答えてください.
この時同時に, 次に何の情報を埋めるべきか, そしてそれをするためには何が必要かのおすすめの情報も常に表示をしなさい.
例えば, 穴埋めするのに情報が十分でないならば何が足りないかを教えてあげててください.


--- 対策シナリオ
{"$schema":"http://json-schema.org/draft-07/schema#","title":"イベント対応対策シナリオ","description":"企業が特定のイベントに対応するために策定する対策シナリオのデータ構造","type":"object","properties":{"strategy_name":{"type":"string","title":"対策シナリオ名","description":"対策シナリオの名称を指定する","example":["関西シナリオ（調達影響）","九州シナリオ（販売影響）","東京シナリオ（生産影響）","物流停止対策","サプライチェーン維持対策"]},"strategy_id":{"type":"string","title":"対策ID","description":"一意の識別子を指定する","examples":["20250914_Kansai_Supply","20250914_Kyushu_Retail","20250914_Tokyo_Manufacturing","YYYYMMDD_Location_Impact"]},"create_date":{"type":"string","format":"date-time","title":"作成日時","description":"対策シナリオが作成された日時。ISO8601形式で記載する","examples":["2025-09-12T10:00:00Z"]},"version":{"type":"string","title":"バージョン","description":"対策シナリオのバージョン管理。変更が加えられた際に更新する","examples":["V1.0","V1.1","V2.0"]},"department":{"type":"string","title":"担当部署","description":"この対策シナリオを管理する部署","examples":["経営企画部","危機管理部","調達部"]},"responsible_person":{"type":"string","title":"責任者","description":"この対策シナリオの責任者の氏名","examples":["財前悠一","田中一郎","佐藤三郎"]},"event":{"type":"object","title":"対象イベント","description":"この対策が対応するイベントの情報","properties":{"impact_level":{"type":"string","enum":["軽度","中度","重大"],"title":"影響度","description":"イベントの影響度,与えられるevent情報から直ちに埋めることができる."},"version":{"type":"string","title":"イベント情報のバージョン","description":"関連するイベント情報のバージョン管理,与えられるevent情報から直ちに埋めることができる.","examples":["V1.2","V1.3"]},"name":{"type":"string","title":"イベント名","description":"発生したイベントの名称,与えられるevent情報から直ちに埋めることができる.","examples":["台風15号直撃の可能性","大規模地震発生","サイバー攻撃の兆候"]},"url":{"type":"string","format":"uri","title":"イベント情報URL,与えられるevent情報から直ちに埋めることができる.","description":"公式発表や関連報告書のURLを記載する"}}},"activation":{"type":"object","title":"発動条件","description":"対策シナリオを発動する条件,初期に通知する人間の選択を実施する","examples":[{"responsible":"経営企画部","time":"09/13深夜","conditions":"台風が関西圏に直撃し、物流・調達に影響を及ぼす場合","metrics":["物流停止時間","影響を受けるサプライヤー数"],"notifications":["調達部","物流部","製造部","営業部"]}]},"initial_response":{"type":"array","title":"初動対応","description":"イベント発生時の最初の対応措置,ここでは今後の対策活動を円滑に実施するための準備を行います.","examples":[{"name":"リアルタイム監視","responsible":"調達部","details":"物流・天候の影響を監視し、緊急アラート発信","risk":"物流停止の見落とし","recovery_action":"迂回ルートの確保"},{"name":"倉庫の在庫確認","responsible":"調達部","details":"関西倉庫の在庫を緊急チェックし、影響範囲を特定","risk":"在庫不足による生産ライン停止","recovery_action":"関東・九州の倉庫からの補充を調整"},{"name":"緊急会議の開催","responsible":"経営企画部","details":"対策シナリオの適用と影響範囲の確認","risk":"初動対応の遅れによる影響拡大","recovery_action":"各部門に迅速な対応を指示"}]},"containment_measures":{"type":"array","title":"封じ込め対策","description":"影響を最小限に抑えるための措置,ここでは被害の拡大を最小限に止めるための活動を実施します.","examples":[{"name":"代替輸送ルートの確保","responsible":"物流部","details":"関東・九州の調達先に供給可能性を確認","risk":"輸送手段の確保失敗","recovery_action":"航空輸送の手配"},{"name":"サプライヤーとの調達交渉","responsible":"経営企画部","details":"追加調達および代替品の確保","risk":"調達遅延による生産影響","recovery_action":"代替サプライヤーの即時手配と契約交渉の加速"},{"name":"優先供給先の決定","responsible":"調達部","details":"影響を受ける取引先を特定し、優先供給計画を策定","risk":"供給不足による顧客満足度低下","recovery_action":"在庫の最適配分と納期調整"}]},"monitoring":{"type":"array","title":"モニタリング","description":"事後の状況監視と対応,ここでは状況の解決のために,状態を安定化させるための仕事に取り組みます.","examples":[{"name":"調達・物流状況の監視","responsible":"調達部","details":"在庫管理の継続","risk":"在庫切れ","recovery_action":"優先供給先の再評価"},{"name":"サプライチェーンの監視","responsible":"経営企画部","details":"物流回復までの影響を分析し、今後の対策を検討","risk":"供給の遅延が長引く可能性","recovery_action":"代替供給計画の策定"},{"name":"市場の影響評価","responsible":"営業部","details":"販売データを収集し、需要変動を監視","risk":"販売機会の損失","recovery_action":"プロモーション施策の調整"}]},"recovery":{"type":"array","title":"復旧計画","description":"通常運用への移行手順,ここでは,具体的な復旧を実施することで,最終的な解決を目指します.","examples":[{"name":"通常調達プロセスへの移行","responsible":"調達部","details":"物流回復後、通常の調達へ戻す","risk":"長期的な影響","recovery_action":"段階的移行計画の策定"},{"name":"影響分析とBCP見直し","responsible":"経営企画部","details":"発生した影響の分析と、今後の事業継続計画（BCP）の改善","risk":"次回の災害時に適切な対応ができない","recovery_action":"新しい対策手順を策定し、関係部門と共有"},{"name":"顧客対応の最適化","responsible":"営業部","details":"顧客との信頼関係維持のため、影響報告と代替対応の説明","risk":"顧客の信頼低下","recovery_action":"事後対応の強化と次回対策の通知"}]]}},"required":["strategy_name","strategy_id","create_date","version","department","responsible_person","event","activation","initial_response","containment_measures","monitoring","recovery"]}

-- 変数を埋める順番の整理
1. 変数ごとの埋める順番とステップ
| 順番 | 変数名 | 自動化の度合い | 作業内容の詳細 | 必要な前提知識 (`event_scenario` のプロパティを含む) | ステップ番号 | ステップ名 |
|----|------------|----------------|----------------------------------|----------------------------------|------------|------------------|
| 1 | `create_date` | 自動 | シナリオ作成日時を現在のタイムスタンプで自動入力 | システムの現在時刻 | 1 | 初期セットアップ |
| 2 | `version` | 自動, または半自動 | 初期バージョンとして `"V1.0"` を自動入力, 過去にすでに資料があればそのバージョンを元にユーザが生成する. | 既定の初期バージョン, または前回設定されたバージョン | 1 | 初期セットアップ |
| 3 | `event.impact_level` | 自動 | `event_scenario.impact_level` をそのまま入力 | `event_scenario.impact_level` | 2 | イベント情報の適用 |
| 4 | `event.version` | 自動 | `event_scenario.version` をそのまま入力 | `event_scenario.version` | 2 | イベント情報の適用 |
| 5 | `event.name` | 自動 | `event_scenario.event_name` をそのまま入力 | `event_scenario.event_name` | 2 | イベント情報の適用 |
| 6 | `event.url` | 自動 | `event_scenario.event_id` に基づき公式情報URLを生成 | `event_scenario.event_id`（公式情報データベースとのマッピング） | 2 | イベント情報の適用 |
| 7 | `strategy_id` | 自動 | `create_date` と `event.name` を組み合わせて一意のIDを生成 | `create_date`、`event.name` | 3 | シナリオ識別情報の生成 |
| 8 | `strategy_name` | 半自動 | `event.name` に基づいて過去の類似シナリオを検索し、候補を提示 | `event.name`、`event.impact_level`（過去事例とのマッチング） | 3 | シナリオ識別情報の生成 |
| 9 | `department` | 自動 | `event_scenario.department` をそのまま入力 | `event_scenario.department` | 4 | 担当者・組織の決定 |
| 10 | `responsible_person` | 自動 | `event_scenario.responsible_person` をそのまま入力 | `event_scenario.responsible_person` | 4 | 担当者・組織の決定 |
| 11 | `activation.responsible` | 半自動 | `department` に基づき、過去の類似シナリオから適切な担当部署を提案 | `department`（過去のシナリオデータ） | 5 | 発動条件の設定 |
| 12 | `activation.time` | 半自動 | `event_scenario.impact_duration.start` と `event_scenario.impact_duration.end` の情報を参考に、影響が出る時間帯を提案 | `event_scenario.impact_duration.start`、`event_scenario.impact_duration.end` | 5 | 発動条件の設定 |
| 13 | `activation.conditions` | 手動 | `event_scenario.overview` や `event_scenario.event_metrics.overview` を参考にしながら、対策発動条件を決定 | `event_scenario.overview`、`event_scenario.event_metrics.overview` | 5 | 発動条件の設定 |
| 14 | `activation.metrics` | 手動 | `event_scenario.event_metrics.risk` を参考に、影響を測るための指標を決定 | `event_scenario.event_metrics.risk` | 5 | 発動条件の設定 |
| 15 | `activation.notifications` | 手動 | 発動時に通知する部門や担当者をリストアップ | `department`、`responsible_person` | 5 | 発動条件の設定 |
| 16 | `initial_response` | 手動 | **初動対応をリストアップし、影響を受けるプロセスごとに具体的な対応を策定する。**`event_scenario.event_metrics.process` や `event.impact_level` をもとに、必要な対応アクション、責任部門、リスク評価、回復措置を記述。事例：「リアルタイム監視」「在庫確認」「緊急会議の開催」など。 | `event_scenario.event_metrics.process`、`event.impact_level` | 6 | 初動対応の策定 |
| 17 | `containment_measures` | 手動 | **影響拡大を防ぐための封じ込め策を策定する。** `event_scenario.event_metrics.process` を参考に、影響を受ける業務領域ごとに、具体的な対応策、責任者、リスク、回復措置を設定。事例：「代替輸送ルートの確保」「サプライヤーとの追加交渉」「優先供給計画の策定」など。 | `event_scenario.event_metrics.process`、`event.impact_level` | 7 | 影響封じ込めの策定 |
| 18 | `monitoring` | 手動 | **イベント影響の長期監視体制を確立する。** `containment_measures` の内容をもとに、影響が続く可能性のある領域の監視方法を策定。責任者、監視対象、リスク管理、回復措置を記述。事例：「物流・調達の監視」「サプライチェーン全体の影響分析」「市場の影響評価」など。 | `containment_measures` の内容 | 8 | 事後対応・監視の策定 |
| 19 | `recovery` | 手動 | **事業を通常運用へ戻すための復旧計画を策定する。** `containment_measures` の結果を踏まえ、正常化に向けた具体的な復旧策を定める。責任者、復旧作業、リスク、回復措置を明確化。事例：「通常調達プロセスへの移行」「事業継続計画（BCP）の見直し」「顧客対応の最適化」など。 | `containment_measures` の結果 | 9 | 復旧計画の策定 |


2. ステップごとの詳細
| ステップ番号 | ステップ名 | ステップの概要 | ステップで実施する作業の内容 |
|------------|------------------|------------------------------------------------|------------------------------------------------------------|
| 1 | 初期セットアップ | シナリオの基本情報を準備する | `create_date` と `version` をシステムから自動入力する, 必要であれば人の手で修正する |
| 2 | イベント情報の適用 | `event_scenario` からイベントの詳細を取り込む | `event.impact_level`、`event.version`、`event.name`、`event.url` を `event_scenario` から取得 |
| 3 | シナリオ識別情報の生成 | シナリオを特定するためのIDや名称を決定 | `strategy_id` を `create_date` と `event.name` から生成し、`strategy_name` を類似事例から候補提案 |
| 4 | 担当者・組織の決定 | シナリオの管理責任者を特定する | `department`、`responsible_person` を `event_scenario` から取得 |
| 5 | 発動条件の設定 | どの条件でシナリオを発動するか決定する | `activation.responsible`、`activation.time`、`activation.conditions`、`activation.metrics`、`activation.notifications` を設定 |
| 6 | 初動対応の策定 | イベント発生直後の対応策を決定する | `initial_response` に **初期の緊急対応策** を定義。`event_scenario.event_metrics.process` を参考に、影響を受ける業務プロセスを特定し、緊急対応を決定。対応の責任部署、具体的な対応内容、対応遅延時のリスク、回復措置を明確化する。例：「物流の監視」「在庫確認」「緊急会議の開催」など。 |
| 7 | 影響封じ込めの策定 | 影響を最小限に抑えるための対策を決定する | `containment_measures` に **被害の拡大を抑えるための対応策** を定義。`event_scenario.event_metrics.process` を参考に、供給網の崩壊や生産停止を防ぐ対策を策定。対策の責任者、詳細、リスク、および回復措置を記述。例：「代替輸送ルートの確保」「サプライヤーとの追加調達交渉」「影響範囲の特定と優先供給先の決定」など。 |
| 8 | 事後対応・監視の策定 | イベント後の影響監視や対応策を決定する | `monitoring` に **イベント発生後の継続的な状況監視** を定義。`containment_measures` の内容を参考にしながら、影響の長期化を防ぐための監視体制を構築する。監視対象のプロセス、責任者、リスク管理、回復措置を記述。例：「調達・物流の監視」「サプライチェーン全体の影響分析」「市場の影響評価」など。 |
| 9 | 復旧計画の策定 | 事業を通常運用へ戻すための計画を立案する | `recovery` に **通常業務へ戻るための具体的な復旧計画** を定義。`containment_measures` の結果を踏まえ、正常化へのロードマップを作成。責任者、詳細、リスク、および回復措置を明確にする。例：「通常調達プロセスへの移行」「影響分析と事業継続計画（BCP）の見直し」「顧客対応の最適化」など。 |



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
            "description": "企業が特定のイベントに対応するために策定する対策シナリオのデータ構造",
            "type": "object",
            "properties": {
                "strategy_name": {
                    "type": "string",
                    "title": "対策シナリオ名",
                    "description": "対策シナリオの名称を指定する",
                    "example": [
                        "関西シナリオ（調達影響）",
                        "九州シナリオ（販売影響）",
                        "東京シナリオ（生産影響）",
                        "物流停止対策",
                        "サプライチェーン維持対策",
                    ],
                },
                "strategy_id": {
                    "type": "string",
                    "title": "対策ID",
                    "description": "一意の識別子を指定する",
                    "example": [
                        "20250914_Kansai_Supply",
                        "20250914_Kyushu_Retail",
                        "20250914_Tokyo_Manufacturing",
                        "YYYYMMDD_Location_Impact",
                    ],
                },
                "create_date": {
                    "type": "string",
                    "format": "date-time",
                    "title": "作成日時",
                    "description": "対策シナリオが作成された日時。ISO 8601形式で記載する",
                    "example": ["2025-09-12T10:00:00Z"],
                },
                "version": {
                    "type": "string",
                    "title": "バージョン",
                    "description": "対策シナリオのバージョン管理。変更が加えられた際に更新する",
                    "example": ["V1.0", "V1.1", "V2.0"],
                },
                "department": {
                    "type": "string",
                    "title": "担当部署",
                    "description": "この対策シナリオを管理する部署",
                    "example": ["経営企画部", "危機管理部", "調達部"],
                },
                "responsible_person": {
                    "type": "string",
                    "title": "責任者",
                    "description": "この対策シナリオの責任者の氏名",
                    "example": ["財前悠一", "田中一郎", "佐藤三郎"],
                },
                "event": {
                    "type": "object",
                    "title": "対象イベント",
                    "description": "この対策が対応するイベントの情報",
                    "properties": {
                        "impact_level": {
                            "type": "string",
                            "enum": ["軽度", "中度", "重大"],
                            "title": "影響度",
                            "description": "イベントの影響度, 与えられるevent情報から直ちに埋めることができる.",
                        },
                        "version": {
                            "type": "string",
                            "title": "イベント情報のバージョン",
                            "description": "関連するイベント情報のバージョン管理, 与えられるevent情報から直ちに埋めることができる.",
                            "example": ["V1.2", "V1.3"],
                        },
                        "name": {
                            "type": "string",
                            "title": "イベント名",
                            "description": "発生したイベントの名称, 与えられるevent情報から直ちに埋めることができる.",
                            "example": [
                                "台風15号直撃の可能性",
                                "大規模地震発生",
                                "サイバー攻撃の兆候",
                            ],
                        },
                        "url": {
                            "type": "string",
                            "format": "uri",
                            "title": "イベント情報URL, 与えられるevent情報から直ちに埋めることができる.",
                            "description": "公式発表や関連報告書のURLを記載する",
                        },
                    },
                },
                "activation": {
                    "type": "object",
                    "title": "発動条件",
                    "description": "対策シナリオを発動する条件, 初期に通知する人間の選択を実施する",
                    "example": [
                        {
                            "responsible": "経営企画部",
                            "time": "09/13 深夜",
                            "conditions": "台風が関西圏に直撃し、物流・調達に影響を及ぼす場合",
                            "metrics": ["物流停止時間", "影響を受けるサプライヤー数"],
                            "notifications": ["調達部", "物流部", "製造部", "営業部"],
                        }
                    ],
                },
                "initial_response": {
                    "type": "array",
                    "title": "初動対応",
                    "description": "イベント発生時の最初の対応措置, ここでは今後の対策活動を円滑に実施するための準備を行います.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "対応アクションの名称",
                            },
                            "responsible": {
                                "type": "string",
                                "description": "対応責任部門",
                            },
                            "details": {
                                "type": "string",
                                "description": "実施する具体的な対応内容",
                            },
                            "risk": {
                                "type": "string",
                                "description": "対応を怠った場合のリスク",
                            },
                            "recovery_action": {
                                "type": "string",
                                "description": "リスク発生時の回復措置",
                            },
                        },
                    },
                    "example": [
                        {
                            "name": "リアルタイム監視",
                            "responsible": "調達部",
                            "details": "物流・天候の影響を監視し、緊急アラート発信",
                            "risk": "物流停止の見落とし",
                            "recovery_action": "迂回ルートの確保",
                        },
                        {
                            "name": "倉庫の在庫確認",
                            "responsible": "調達部",
                            "details": "関西倉庫の在庫を緊急チェックし、影響範囲を特定",
                            "risk": "在庫不足による生産ライン停止",
                            "recovery_action": "関東・九州の倉庫からの補充を調整",
                        },
                        {
                            "name": "緊急会議の開催",
                            "responsible": "経営企画部",
                            "details": "対策シナリオの適用と影響範囲の確認",
                            "risk": "初動対応の遅れによる影響拡大",
                            "recovery_action": "各部門に迅速な対応を指示",
                        },
                    ],
                },
                "containment_measures": {
                    "type": "array",
                    "title": "封じ込め対策",
                    "description": "影響を最小限に抑えるための措置, ここでは被害の拡大を最小限に止めるための活動を実施します.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "対策名"},
                            "responsible": {"type": "string", "description": "責任者"},
                            "details": {"type": "string", "description": "対策の詳細"},
                            "risk": {"type": "string", "description": "リスクの概要"},
                            "recovery_action": {
                                "type": "string",
                                "description": "リスク発生時の対応措置",
                            },
                        },
                    },
                    "example": [
                        {
                            "name": "代替輸送ルートの確保",
                            "responsible": "物流部",
                            "details": "関東・九州の調達先に供給可能性を確認",
                            "risk": "輸送手段の確保失敗",
                            "recovery_action": "航空輸送の手配",
                        },
                        {
                            "name": "サプライヤーとの調達交渉",
                            "responsible": "経営企画部",
                            "details": "追加調達および代替品の確保",
                            "risk": "調達遅延による生産影響",
                            "recovery_action": "代替サプライヤーの即時手配と契約交渉の加速",
                        },
                        {
                            "name": "優先供給先の決定",
                            "responsible": "調達部",
                            "details": "影響を受ける取引先を特定し、優先供給計画を策定",
                            "risk": "供給不足による顧客満足度低下",
                            "recovery_action": "在庫の最適配分と納期調整",
                        },
                    ],
                },
                "monitoring": {
                    "type": "array",
                    "title": "モニタリング",
                    "description": "事後の状況監視と対応, ここでは状況の解決のために, 状態を安定化させるための仕事に取り組みます.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "対策名"},
                            "responsible": {"type": "string", "description": "責任者"},
                            "details": {"type": "string", "description": "対策の詳細"},
                            "risk": {"type": "string", "description": "リスクの概要"},
                            "recovery_action": {
                                "type": "string",
                                "description": "リスク発生時の対応措置",
                            },
                        },
                    },
                    "example": [
                        {
                            "name": "調達・物流状況の監視",
                            "responsible": "調達部",
                            "details": "在庫管理の継続",
                            "risk": "在庫切れ",
                            "recovery_action": "優先供給先の再評価",
                        },
                        {
                            "name": "サプライチェーンの監視",
                            "responsible": "経営企画部",
                            "details": "物流回復までの影響を分析し、今後の対策を検討",
                            "risk": "供給の遅延が長引く可能性",
                            "recovery_action": "代替供給計画の策定",
                        },
                        {
                            "name": "市場の影響評価",
                            "responsible": "営業部",
                            "details": "販売データを収集し、需要変動を監視",
                            "risk": "販売機会の損失",
                            "recovery_action": "プロモーション施策の調整",
                        },
                    ],
                },
                "recovery": {
                    "type": "array",
                    "title": "復旧計画",
                    "description": "通常運用への移行手順, ここでは, 具体的な復旧を実施することで, 最終的な解決を目指します.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "復旧アクションの名称",
                            },
                            "responsible": {
                                "type": "string",
                                "description": "対応責任部門",
                            },
                            "details": {
                                "type": "string",
                                "description": "復旧作業の具体的な内容",
                            },
                            "risk": {
                                "type": "string",
                                "description": "復旧遅延や問題発生時のリスク",
                            },
                            "recovery_action": {
                                "type": "string",
                                "description": "復旧プロセスを円滑に進めるための対応策",
                            },
                        },
                    },
                    "example": [
                        {
                            "name": "通常調達プロセスへの移行",
                            "responsible": "調達部",
                            "details": "物流回復後、通常の調達へ戻す",
                            "risk": "長期的な影響",
                            "recovery_action": "段階的移行計画の策定",
                        },
                        {
                            "name": "影響分析とBCP見直し",
                            "responsible": "経営企画部",
                            "details": "発生した影響の分析と、今後の事業継続計画（BCP）の改善",
                            "risk": "次回の災害時に適切な対応ができない",
                            "recovery_action": "新しい対策手順を策定し、関係部門と共有",
                        },
                        {
                            "name": "顧客対応の最適化",
                            "responsible": "営業部",
                            "details": "顧客との信頼関係維持のため、影響報告と代替対応の説明",
                            "risk": "顧客の信頼低下",
                            "recovery_action": "事後対応の強化と次回対策の通知",
                        },
                    ],
                },
            },
            "required": [
                "strategy_name",
                "strategy_id",
                "create_date",
                "version",
                "department",
                "responsible_person",
                "event",
                "activation",
                "initial_response",
                "containment_measures",
                "monitoring",
                "recovery",
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

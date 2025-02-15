 **ステップ**
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

---

**変数の設定方法**
| 変数名 | 自動化の度合い | 作業内容の詳細 | 必要な前提知識 (`event_scenario` のプロパティを含む) | ステップ番号 | ステップ名 |
|------------|----------------|----------------------------------|----------------------------------|------------|------------------|
| `create_date` | 自動 | シナリオ作成日時を現在のタイムスタンプで自動入力 | システムの現在時刻 | 1 | 初期セットアップ |
| `version` | 自動, または半自動 | 初期バージョンとして `"V1.0"` を自動入力, 過去にすでに資料があればそのバージョンを元にユーザが生成する. | 既定の初期バージョン, または前回設定されたバージョン | 1 | 初期セットアップ |
| `event.impact_level` | 自動 | `event_scenario.impact_level` をそのまま入力 | `event_scenario.impact_level` | 2 | イベント情報の適用 |
| `event.version` | 自動 | `event_scenario.version` をそのまま入力 | `event_scenario.version` | 2 | イベント情報の適用 |
| `event.name` | 自動 | `event_scenario.event_name` をそのまま入力 | `event_scenario.event_name` | 2 | イベント情報の適用 |
| `event.url` | 自動 | `event_scenario.event_id` に基づき公式情報URLを生成 | `event_scenario.event_id`（公式情報データベースとのマッピング） | 2 | イベント情報の適用 |
| `strategy_id` | 自動 | `create_date` と `event.name` を組み合わせて一意のIDを生成 | `create_date`、`event.name` | 3 | シナリオ識別情報の生成 |
| `strategy_name` | 半自動 | `event.name` に基づいて過去の類似シナリオを検索し、候補を提示 | `event.name`、`event.impact_level`（過去事例とのマッチング） | 3 | シナリオ識別情報の生成 |
| `department` | 自動 | `event_scenario.department` をそのまま入力 | `event_scenario.department` | 4 | 担当者・組織の決定 |
| `responsible_person` | 自動 | `event_scenario.responsible_person` をそのまま入力 | `event_scenario.responsible_person` | 4 | 担当者・組織の決定 |
| `activation.responsible` | 半自動 | `department` に基づき、過去の類似シナリオから適切な担当部署を提案 | `department`（過去のシナリオデータ） | 5 | 発動条件の設定 |
| `activation.time` | 半自動 | `event_scenario.impact_duration.start` と `event_scenario.impact_duration.end` の情報を参考に、影響が出る時間帯を提案 | `event_scenario.impact_duration.start`、`event_scenario.impact_duration.end` | 5 | 発動条件の設定 |
| `activation.conditions` | 手動 | `event_scenario.overview` や `event_scenario.event_metrics.overview` を参考にしながら、対策発動条件を決定 | `event_scenario.overview`、`event_scenario.event_metrics.overview` | 5 | 発動条件の設定 |
| `activation.metrics` | 手動 | `event_scenario.event_metrics.risk` を参考に、影響を測るための指標を決定 | `event_scenario.event_metrics.risk` | 5 | 発動条件の設定 |
| `activation.notifications` | 手動 | 発動時に通知する部門や担当者をリストアップ | `department`、`responsible_person` | 5 | 発動条件の設定 |
| `initial_response` | 手動 | **初動対応をリストアップし、影響を受けるプロセスごとに具体的な対応を策定する。**`event_scenario.event_metrics.process` や `event.impact_level` をもとに、必要な対応アクション、責任部門、リスク評価、回復措置を記述。事例：「リアルタイム監視」「在庫確認」「緊急会議の開催」など。 | `event_scenario.event_metrics.process`、`event.impact_level` | 6 | 初動対応の策定 |
| `containment_measures` | 手動 | **影響拡大を防ぐための封じ込め策を策定する。** `event_scenario.event_metrics.process` を参考に、影響を受ける業務領域ごとに、具体的な対応策、責任者、リスク、回復措置を設定。事例：「代替輸送ルートの確保」「サプライヤーとの追加交渉」「優先供給計画の策定」など。 | `event_scenario.event_metrics.process`、`event.impact_level` | 7 | 影響封じ込めの策定 |
| `monitoring` | 手動 | **イベント影響の長期監視体制を確立する。** `containment_measures` の内容をもとに、影響が続く可能性のある領域の監視方法を策定。責任者、監視対象、リスク管理、回復措置を記述。事例：「物流・調達の監視」「サプライチェーン全体の影響分析」「市場の影響評価」など。 | `containment_measures` の内容 | 8 | 事後対応・監視の策定 |
| `recovery` | 手動 | **事業を通常運用へ戻すための復旧計画を策定する。** `containment_measures` の結果を踏まえ、正常化に向けた具体的な復旧策を定める。責任者、復旧作業、リスク、回復措置を明確化。事例：「通常調達プロセスへの移行」「事業継続計画（BCP）の見直し」「顧客対応の最適化」など。 | `containment_measures` の結果 | 9 | 復旧計画の策定 |

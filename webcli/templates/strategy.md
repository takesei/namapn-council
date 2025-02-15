## {{ name }} 対策
- **ID:** `{{ id }}`
- **発行日:** {{ issue_date }} (version {{ version }})
- **担当部門:** `{{ department }}` (責任者: `{{ responsible_person }}` )
- **対応イベント**: {% if event %}[\[`{{ event.impact_level }}`\] {{ event.name }}(`{{ event.version }}`)]({{ event.url }}) {% endif %}

### 起動条件
- **担当:** `{{ activation.responsible }}`
- **通知対象:** {% for target in activation.notifications %} `{{ target }}` {% endfor %}  
- **判断方法**
  - 概要: {{ activation.conditions }}
  - 時期: {{ activation.time }}
  - 基準:
{% for metric in activation.metrics %}
    - {{ metric }}
{% endfor %}


### 対策方針
{% for policy in policies %}
- **{{ policy }}**
{% endfor %}

### 対応手順
#### (1) 初動対応
{% if not initial_response %}
`ここでは今後の対策活動を円滑に実施するための準備を行います.`
{% endif %}
| 名称 | 担当 | 内容 | リスク | リスク対応 |
| ---- | ---- | ---- | ------ | ---------- |
{% for action in initial_response %}
|**{{ action.name }}**| `{{ action.responsible }}` | {{ action.details }} | {{ action.risk }} | {{ action.recovery_action }} |
{% endfor %}

#### (2) 一時対策
{% if not containment_measures %}
`ここでは被害の拡大を最小限に止めるための活動を実施します.`
{% endif %}
| 名称 | 担当 | 内容 | リスク | リスク対応 |
| ---- | ---- | ---- | ------ | ---------- |
{% for action in containment_measures %}
|**{{ action.name }}**| `{{ action.responsible }}` | {{ action.details }} | {{ action.risk }} | {{ action.recovery_action }} |
{% endfor %}

#### (3) 維持
{% if not monitoring %}
`ここでは状況の解決のために, 状態を安定化させるための仕事に取り組みます.`
{% endif %}
{% for action in monitoring %}
| 名称 | 担当 | 内容 | リスク | リスク対応 |
| ---- | ---- | ---- | ------ | ---------- |
|**{{ action.name }}**| `{{ action.responsible }}` | {{ action.details }} | {{ action.risk }} | {{ action.recovery_action }} |
{% endfor %}

#### (4) 復旧プロセス
{% if not recovery %}
`ここでは, 具体的な復旧を実施することで, 最終的な解決を目指します.`
{% endif %}
| 名称 | 担当 | 内容 | リスク | リスク対応 |
| ---- | ---- | ---- | ------ | ---------- |
{% for action in recovery %}
|**{{ action.name }}**| `{{ action.responsible }}` | {{ action.details }} | {{ action.risk }} | {{ action.recovery_action }} |
{% endfor %}

### 参考資料
- **イベントシナリオ**: [{{ event.name }}](event.url)
{% for ref in references %}
- [{{ ref.name }}]({{ ref.url }})
{% endfor %}

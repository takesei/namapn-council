# {{ name }} 概要
- **id:** `{{ id }}`
- **発行日:** {{ issue_date }} (version {{ version }})
- **担当部門:** `{{ department }}` (責任者: `{{ responsible_person }}` )
- **影響度:** `{{ impact_level }}`

## 予測されるイベント情報
- **概要**: {{ overview }}
- **期間:** {{ impact_duration["start"] }} ~ {{ impact_duration["end"] }}
- **エビデンス**:
{% for evidence in evidences %}
  - [{{ evidence.name }}]({{ evidence.url }})
{% endfor %}

{% if timeline %}
### タイムライン
| **時間** | **状況** | **想定される影響** |
|----------|----------|------------------|
{% for phase in timeline %}
| {{ phase.time }} | {{ phase.status }} | {{ phase.impact }} |
{% endfor %}
{% endif %}

{#
    ## 2. 想定されるケースの影響予測
    {% if event_cases %}
    | バージョン | {% for case in event_cases %} [case{{ loop.index }}] {{ case.version }} | {% endfor %}  
    | --- | {% for _ in event_cases %}--- | {% endfor %}  
    {% for attr, label in event_metrics.items() %}
    | {{ label }} | {% for case in event_cases %}{{ case[attr] }} | {% endfor %}  
    {% endfor %}
    {% endif %}
#}

## 参考資料
{% for ref in references %}
- [{{ ref.name }}]({{ ref.url }})
{% endfor %}


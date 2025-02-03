# 📌 インシデントシナリオ: {{ incident_name | default("**未設定**") }}

## 1. タイトル / ID
- **インシデント名:** {{ incident_name | default("**未設定**") }}
- **ID:** {{ incident_id | default("**未設定**") }}
- **発行日:** {{ issue_date | default("**未設定**") }}
- **バージョン:** {{ version | default("**未設定**") }}
- **担当部署:** {{ department | default("**未設定**") }}
- **責任者:** {{ responsible_person | default("**未設定**") }}

## 2. 予測される発生日時 / 期間
- **発生日時:** {{ incident_date | default("**未設定**") }}
- **影響が続く期間:** {{ duration | default("**未設定**") }}

## 3. インシデントの背景・状況
- **発生確定の根拠:** {{ evidence | default("**未設定**") }}
{% if past_incidents %}
- **過去の類似事象:** 
  {% for incident in past_incidents %}
  - {{ incident }}
  {% endfor %}
{% else %}
  - **未設定**
{% endif %}

## 4. 影響範囲（被害予測）

### 4.1 インシデントの深刻度
- **深刻度:** {{ severity | default("**未設定**") }}

### 4.2 影響の確率
{% if impact_probabilities %}
{% for region, probability in impact_probabilities.items() %}
- **{{ region }}:** {{ probability }}%
{% endfor %}
{% else %}
- **未設定**
{% endif %}

### 4.3 影響の詳細
{% if impact_details %}
{% for region, details in impact_details.items() %}
#### ✅ **{{ region }}**
{% for detail in details %}
- {{ detail }}
{% endfor %}
{% endfor %}
{% else %}
- **未設定**
{% endif %}

### 4.4 影響するビジネスプロセス
{% if affected_business_processes %}
{% for region, process in affected_business_processes.items() %}
- **{{ region }}:** {{ process }}
{% endfor %}
{% else %}
- **未設定**
{% endif %}

### 4.5 リスク評価
- **予測売上損失:** {{ estimated_loss | default("**未設定**") }}  
- **納期遅延の影響:** {{ delivery_impact | default("**未設定**") }}  

## 5. 時系列(フェーズ)予測
| **時間** | **状況** | **想定される影響** |
|----------|----------|------------------|
{% if timeline %}
{% for phase in timeline %}
| {{ phase.time | default("**未設定**") }} | {{ phase.status | default("**未設定**") }} | {{ phase.impact | default("**未設定**") }} |
{% endfor %}
{% else %}
| **未設定** | **未設定** | **未設定** |
{% endif %}

## 6. ダメコンシナリオへの導線
{% if damage_control_scenarios %}
- **該当するダメコンシナリオ:**  
{% for scenario in damage_control_scenarios %}
- {{ scenario }}
{% endfor %}
{% else %}
- **未設定**
{% endif %}

## 7. 参考資料
- **関連マニュアル・BCP文書:** {{ related_manuals | default("**未設定**") }}  
- **社内外のリアルタイム情報:** {{ real_time_info | default("**未設定**") }}

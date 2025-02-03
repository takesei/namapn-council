# 📌 戦略シナリオ: {{ scenario_name | default("**未設定**") }}

## 1. シナリオ名 / ID / 適用条件
- **シナリオ名:** {{ scenario_name | default("**未設定**") }}
- **ID:** {{ scenario_id | default("**未設定**") }}
- **適用条件:** {{ conditions | default("**未設定**") }}
- **深刻度:** {{ severity | default("**未設定**") }}

## 2. 目的
{% if objectives %}
  {% for objective in objectives %}
  - **{{ objective }}**
  {% endfor %}
{% else %}
  - **未設定**
{% endif %}

## 3. 手順・フロー

### (1) アクティベーション（発動）
{% if activation %}
- **責任者:** {{ activation.responsible | default("**未設定**") }}
- **判断基準:** {{ activation.criteria | default("**未設定**") }}
- **通知:** {{ activation.notifications | join(", ") | default("**未設定**") }}
{% else %}
  - **未設定**
{% endif %}

### (2) 初動対応 (0〜30分)
{% if initial_response %}
  {% for action in initial_response %}
- **{{ action.name | default("**未設定**") }}**  
  - **担当:** {{ action.responsible | default("**未設定**") }}  
  - **内容:** {{ action.details | default("**未設定**") }}
  {% endfor %}
{% else %}
  - **未設定**
{% endif %}

### (3) 封じ込め・一時対策 (30分〜数時間)
{% if containment_measures %}
  {% for action in containment_measures %}
- **{{ action.name | default("**未設定**") }}**  
  - **担当:** {{ action.responsible | default("**未設定**") }}  
  - **内容:** {{ action.details | default("**未設定**") }}
  {% endfor %}
{% else %}
  - **未設定**
{% endif %}

### (4) 維持・モニタリング (数時間〜収束まで)
{% if monitoring %}
  {% for action in monitoring %}
- **{{ action.name | default("**未設定**") }}**  
  - **担当:** {{ action.responsible | default("**未設定**") }}  
  - **内容:** {{ action.details | default("**未設定**") }}
  {% endfor %}
{% else %}
  - **未設定**
{% endif %}

### (5) 復旧プロセス・フォローアップ
{% if recovery %}
  {% for action in recovery %}
- **{{ action.name | default("**未設定**") }}**  
  - **担当:** {{ action.responsible | default("**未設定**") }}  
  - **内容:** {{ action.details | default("**未設定**") }}
  {% endfor %}
{% else %}
  - **未設定**
{% endif %}

## 4. リスクと分岐（他シナリオへの切り替え）
{% if risks_and_alternatives %}
  {% for risk in risks_and_alternatives %}
- **{{ risk.scenario | default("**未設定**") }}:** {{ risk.details | default("**未設定**") }}
  {% endfor %}
{% else %}
  - **未設定**
{% endif %}

## 5. コミュニケーション計画
{% if communication_plan %}
  {% for plan in communication_plan %}
- **{{ plan.target | default("**未設定**") }}:**  
  - **担当:** {{ plan.responsible | default("**未設定**") }}  
  - **内容:** {{ plan.details | default("**未設定**") }}
  {% endfor %}
{% else %}
  - **未設定**
{% endif %}

## 6. 関連リンク・詳細資料
- **インシデントシナリオ:** {{ related_incident | default("**未設定**") }}
{% if additional_references %}
  {% for reference in additional_references %}
- **{{ reference.name | default("**未設定**") }}:** {{ reference.link | default("**未設定**") }}
  {% endfor %}
{% else %}
  - **未設定**
{% endif %}

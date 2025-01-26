import functions_framework
from google.cloud import bigquery
from flask import Request, jsonify


@functions_framework.http
def execute_bq_query(request: Request) -> int | str:
    inp = request.json
    if inp is None:
        return 400

    pj_id = "velvety-outcome-448307-f0"
    client = bigquery.Client(project=pj_id)  # Initialize BigQuery client

    df = client.query_and_wait(inp["query"]).to_dataframe().to_json()

    return jsonify(dict(data=df))

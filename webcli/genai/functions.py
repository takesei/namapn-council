import requests


def run_bq_query(query: str) -> str:
    """デプロイ済みの Cloud Run/Functions を呼び出すための関数"""

    print("Query from LLM")
    print(query)
    print("==============\n")

    # Endpoint of Cloud Functions
    url = "https://execute-bq-query-42822254114.us-west1.run.app"

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={"query": query},
        timeout=10,
    )

    if response.status_code == 200:
        data = response.json()
        return response.text if data is None else data["data"]

    else:
        raise RuntimeError(
            f"Error: status code {response.status_code}, body={response.text}"
        )

def load_spread_sheet(url: str) -> None:
    ...

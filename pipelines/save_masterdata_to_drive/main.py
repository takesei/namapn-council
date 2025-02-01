import json
import requests
import functions_framework
from flask import Request, jsonify

@functions_framework.http
def save_masterdata_to_drive(request: Request):
    pj_id = "velvety-outcome-448307-f0"

    inp = request.json

    master_data_name = None
    if inp["master_data_name"] is not None:
        master_data_name = inp["master_data_name"]

    if master_data_name is None:
        print("Error request body has no master_data_name field")
        raise Exception()
    
    drive_folder_id = None
    if inp["drive_folder_id"] is not None:
        drive_folder_id = inp["drive_folder_id"]

    if drive_folder_id is None:
        print("Error request body has no drive_folder_id field")
        raise Exception()

    try:
        response = requests.post(
            f"https://us-west1-{pj_id}.cloudfunctions.net/get_spread_sheet_urls",
            params={"folder_id": drive_folder_id}
        )
        sheets = response.json()
    except Exception as e:
        print('get-spread-sheet-urls呼び出し時にエラーが発生しました．')
        raise e; 

    for sheet_name, sheet_id in sheets.items():
        print(f"{sheet_name}: {sheet_id}")
        table_name = sheet_name.split('.')[0]
        try:
            response = requests.post(
                f"https://us-west1-{pj_id}.cloudfunctions.net/execute_bq_query",
                data=json.dumps({"query": f"select * from {master_data_name}.{table_name}"}),
                headers={"Content-Type": "application/json"},
            )
            if not response.ok:
                raise Exception('')
        except Exception as e:
            print(f"failed to get {master_data_name}.{table_name}")
            raise e

        try:
            response = requests.post(
                f"https://us-west1-{pj_id}.cloudfunctions.net/update_spread_sheet",
                data=json.dumps({
                    "file_id": sheet_id,
                    "file_contents": response.json()
                })
            )
            if not response.ok:
                raise Exception()
        except Exception as e:
            print(f"failed to update sheet_id: {sheet_id}, contents: {response.json()}")
            raise e

    return jsonify(dict(msg="ok"))

import json
import os
import requests
import functions_framework
from flask import Request, jsonify
import pandas as pd

@functions_framework.http
def save_masterdata_to_drive(request: Request):
    pj_id = "velvety-outcome-448307-f0"

    inp = request.json

    master_data_name = os.environ["DEFAULT_MASTER_DATA_NAME"] if inp.get("master_data_name") is None else inp.get("master_data_name")
    drive_folder_id = os.environ["DEFAULT_DRIVE_FOLDER_ID"] if inp.get("drive_folder_id") is None else inp.get("drive_folder_id")

    print(dict(
        master_data_name=master_data_name,
        drive_folder_id=drive_folder_id,
    ))

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
            bq_response = requests.post(
                f"https://us-west1-{pj_id}.cloudfunctions.net/execute_bq_query",
                data=json.dumps({"query": f"select * from {master_data_name}.{table_name}"}),
                headers={"Content-Type": "application/json"},
            )
            if not response.ok:
                raise Exception('')
        except Exception as e:
            print(f"failed to get {master_data_name}.{table_name}")
            raise e
        
        bq_data = bq_response.json()
        sheet_csv = pd.DataFrame(json.loads(bq_data['data'])).to_csv(index=False)

        try:
            print('start')
            sheet_response = requests.post(
                f"https://us-west1-{pj_id}.cloudfunctions.net/update_spread_sheet",
                data=json.dumps({
                    "file_id": sheet_id,
                    "file_contents": sheet_csv,
                }),
                headers={"Content-Type": "application/json"},
            )
            print('end')
            if not sheet_response.ok:
                raise Exception()
        except Exception as e:
            print(f"failed to update sheet_id: {sheet_id}, contents: {sheet_csv}")
            raise e

    return jsonify(dict(msg="ok"))

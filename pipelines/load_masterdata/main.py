import pandas as pd
from typing import Any
import requests
from io import BytesIO
from google.cloud import storage
from google.cloud import bigquery
import functions_framework
from flask import Request, jsonify

from .dataset import datasets


def download_and_load_dataframe(url: str, **kwargs: Any) -> pd.DataFrame:
    """read url data as csv file, return dataframe"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        data_bytes = BytesIO(response.content)
        return pd.read_csv(data_bytes, **kwargs)
    except Exception as e:
        print("Error downloading files: {e}")
        raise e


def upload_dataframe_to_gcs(client, df: pd.DataFrame, bucket_name: str, blob_name: str):
    """upload in-memory dataframe to gcs"""
    try:
        csv_data = BytesIO()
        df.to_csv(csv_data, index=False)
        csv_data.seek(0)

        blob = client.bucket(bucket_name).blob(blob_name)
        blob.upload_from_file(csv_data, content_type="text/csv")
        print(f"DataFrame uploaded successfully to gs://{bucket_name}/{blob_name}")
    except Exception as e:
        print(f"Error uploading DataFrame to GCS: {e}")
        raise e


def load_data_from_gcs_to_bigquery(
    client, bucket_name: str, blob_name: str, dataset_name: str, pj_id: str
):
    try:
        uri = f"gs://{bucket_name}/{blob_name}.csv"

        dataset_id = f"{pj_id}.{dataset_name}"
        table_id = f"{dataset_id}.{blob_name}"

        try:
            client.get_table(table_id)
            print(f"Table {table_id} exists. Proceeding with data load.")
        except Exception:
            print(f"Table {table_id} does not exist. Creating table...")
            table = bigquery.Table(table_id)
            client.create_table(table)
            print(f"Table {dataset_id}.{table_id} created successfully.")

        load_job = client.load_table_from_uri(
            uri,
            table_id,
            job_config=bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                autodetect=True,
                skip_leading_rows=1,
                write_disposition="WRITE_APPEND",
            ),
        )

        load_job.result()

        print(f"Data loaded successfully to {dataset_id}.{table_id}")
    except Exception as e:
        print(f"Error loading data to BigQuery: {e}")
        raise e


@functions_framework.http
def load_masterdata(request: Request):
    bucket_name = "planning-master-data"
    pj_id = "velvety-outcome-448307-f0"
    gcs_client = storage.Client(project=pj_id)
    bq_client = bigquery.Client(project=pj_id)

    for dataset_name, files in datasets.items():
        for name, url in files.items():
            print(url)
            try:
                df = download_and_load_dataframe(url)
                upload_dataframe_to_gcs(gcs_client, df, bucket_name, f"{name}.csv")
                load_data_from_gcs_to_bigquery(
                    bq_client, bucket_name, name, dataset_name, pj_id
                )
            except Exception as e:
                print(f"Error at {name}")
                raise e

    return jsonify(dict(msg="ok"))

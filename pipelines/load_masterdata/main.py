import pandas as pd
import requests
from io import BytesIO
from google.cloud import storage
from google.cloud import bigquery
import functions_framework
from flask import Request, jsonify


def download_and_load_dataframe(url, file_type="csv", **kwargs):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data_bytes = BytesIO(response.content)

        if file_type == "csv":
            df = pd.read_csv(data_bytes, **kwargs)
        elif file_type in ["xls", "xlsx", "excel"]:
            df = pd.read_excel(data_bytes, **kwargs)
        else:
            raise ValueError(f"Unsupported file_type: {file_type}")

        return df
    except Exception as e:
        print(f"Error: {e}")
        raise e
        return None


def upload_dataframe_to_gcs(client, df, bucket_name, destination_blob_name):
    try:
        # Convert the DataFrame to a CSV in memory
        csv_data = BytesIO()
        df.to_csv(csv_data, index=False)
        csv_data.seek(0)  # Move the cursor to the beginning of the file-like object

        # Get the bucket and the blob
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # Upload the in-memory file to GCS
        blob.upload_from_file(csv_data, content_type="text/csv")
        print(
            f"DataFrame uploaded successfully to gs://{bucket_name}/{destination_blob_name}"
        )
    except Exception as e:
        print(f"Error uploading DataFrame to GCS: {e}")
        raise e


def load_data_from_gcs_to_bigquery(
    client, bucket_name, source_blob_name, dataset_name, pj_id
):
    dataset_id = f"{pj_id}.{dataset_name}"
    try:
        # Construct the URI for the GCS file
        uri = f"gs://{bucket_name}/{source_blob_name}.csv"

        # Use source_blob_name as table_id
        table_id = f'{pj_id}.{dataset_name}.{source_blob_name.replace("/", "_")}'  # Replace '/' with '_' for valid table name

        try:
            client.get_table(table_id)  # Check if table exists
            print(f"Table {table_id} exists. Proceeding with data load.")
        except Exception:
            print(f"Table {table_id} does not exist. Creating table...")

            # Create an empty table with autodetect schema
            table = bigquery.Table(table_id)
            client.create_table(table)
            print(f"Table {dataset_id}.{table_id} created successfully.")

        # Configure the load job
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            autodetect=True,  # Automatically detect schema
            skip_leading_rows=1,  # Skip header row
            write_disposition="WRITE_TRUNCATE",
        )

        # Load data from GCS to BigQuery
        load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()  # Wait for the job to complete

        print(f"Data loaded successfully to {dataset_id}.{table_id}")
    except Exception as e:
        print(f"Error loading data to BigQuery: {e}")
        raise e


url_head = "https://docs.google.com/spreadsheets/d"
url_tail = "export?format=csv"
file_ids = dict(
    finished_goods="1H6dIv0vHW9x7onsVpuMrUNNSHWaWBUH8",
    materials="1EYyObI5iqmwF1a63Ujiak5-VI2_kBFJJ",
    item_types="15mFCkcWvH_QwL1D4FXA9pt8tXRkKMrP5",
    items="1bxcJ__6cMIQKujigDTe6TGTxea8VPZOP",
    companies="1Ec1V0KxMiBIwiyXDMoYwiCwpmryG75EU",
    customers="1UhFnvCOclKNM_gDmHiR6ExnQOiQtumFV",
    plants="1KHy_OLcKxBJ4zRPZbLqR0h6WytkqXrD0j3ELMtm0GJI",
    locations="1Xd4CzVXXm69dHV5m-9pg4vmrF72_7RUHzJtGuFE4mlE",
    storages="120zkxHHgPUHhPvgI50Ue3xDNaPfp0621",
    lines="1rb2DtvRl_Nuoc1ybfeL_-GkCfFuWa5O5",
    years="1xwd2meOEHd9E_G3cVu8npj3A5RomvH2HPWrl-sAvodY",
    months="1vEIsBhBdcPShF1d-S4jkhAHETAVgvqE5dOFLepsQfOg",
    dates="1Ct8R4LRzhhXJf_B27GN8YTsEL_z5ank6wISTxBya2Fc",
    transactions="1TiLfW6Awf_MKxz88VcKS0X3TWFJFIXcA69p2-xPYJZU",
    transaction_types="1gak_bKvsJhcqYDN43BvF6m83XREJfdePQvn_LwqyWk4",
    bom_trees="1NG8pYZ-OfTyukfY14phYAHpUMbQsK8IoU1SHFhy6AU8",
    sales_forecast="1pJOqpd1MVY-zLXfA7I8t2ITwBEGnuHOPeqpNDWn5lzU",
    sales_plan="1L7L_eZuuJJ6-DRi43ZBzEEnmHSbfbU2De8PrvJfY61Q",
    production_plan="14hln--IN3ckbJws9jHyvTqDdnuw1Gb_bRD84q9XhIpk",
    resource_forecast="1vb9rgryFtnJ_akKou3woD4zrtjYD5qcEf4fWCHhAqyM",
)

# https://drive.google.com/drive/folders/1kXszjwKN9THpzNhAcwwW2Nu2jReNzngP
file_ids_ordinary_v1 = dict(
    finished_goods="",
    materials="",
    item_types="",
    items="",
    companies="",
    customers="",
    plants="",
    locations="",
    storages="",
    lines="",
    years="",
    months="",
    dates="",
    transactions="",
    transaction_types="",
    bom_trees="",
    sales_forecast="",
    sales_plan="",
    production_plan="",
    resource_forecast="",
)

# https://drive.google.com/drive/folders/1p415xgKVNUbI8d5wcMVe6tP2By8EQRKK
file_ids_diaster_v1 = dict(
    finished_goods="",
    materials="",
    item_types="",
    items="",
    companies="",
    customers="",
    plants="",
    locations="",
    storages="",
    lines="",
    years="",
    months="",
    dates="",
    transactions="",
    transaction_types="",
    bom_trees="",
    sales_forecast="",
    sales_plan="",
    production_plan="",
    resource_forecast="",
)

datasets = dict(
    master_data_ordinary=file_ids_ordinary_v1,
    master_data_disaster=file_ids_diaster_v1,
)


@functions_framework.http
def load_masterdata(request: Request):
    bucket_name = "planning-master-data"  # Replace with your GCS bucket name
    pj_id = "velvety-outcome-448307-f0"
    gcs_client = storage.Client(project=pj_id)  # Initialize the GCS client
    bq_client = bigquery.Client(project=pj_id)  # Initialize BigQuery client

    for dataset_name, file_ids in datasets.items():
        for file_name, file_id in file_ids.items():
            url = f"{url_head}/{file_id}/{url_tail}"
            print(url)
            try:
                df = download_and_load_dataframe(url)
                upload_dataframe_to_gcs(gcs_client, df, bucket_name, f"{file_name}.csv")
                load_data_from_gcs_to_bigquery(
                    bq_client, bucket_name, file_name, dataset_name, pj_id
                )
            except Exception as e:
                print(f"Error at {file_name}")
                raise e

    return jsonify(dict(msg="ok"))

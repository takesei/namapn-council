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
    finished_goods="1AojYA4owj9uHG9LtLJO0UofD0b5nqQmD",
    materials="1YLEWXn4t3F5QiSkCMC7Y82-yv-ikFBpX",
    item_types="1bgFIMmXGwt6WHRTj-iqxdLa22KFeW33G",
    items="1AMlMpEsFhDOZsSOcreZ0nWczyKEqsYDE",
    companies="157bxFyNk0raurSg3Tkdt5ZX59WIO8AVF",
    customers="1tn7PQ66Nh52oLAUPDoo4cLhaF8VMGeC6",
    plants="1VDA-aawDfD9aRMaFdl-srcA9J3gVvn2h",
    locations="1NMgsgPVwL-umbNCkvsT1UANhJ2vOhK24",
    storages="1fr_62nhKgqgG_jyGhvK6GXX-9Y0JoE-a",
    lines="12OFFddfL_4j-SLcP9N3fV61NPg2R1e6Y",
    years="17ZBTrRAbFajURMuZ5KfBVq6A1pe3Wx02",
    months="1UqIYBAMo5K_mTaN5CE8QorvtloL57D9_",
    dates="1Yff_Cu4fSWnRGERQ--jYduFA0MUemR4R",
    transactions="1csI3yobyXuOuxsG0lHIvTvV274eu8KN5",
    transaction_types="11aoM0Du7oa4YIAtqxtcursMVlEmreYY4",
    bom_trees="1tqDXImHFKU_SxdQLVyhfCa0qQL-BhMN5",
    sales_forecast="1bL9SNnhAdewsU6z-dWbNUSpGtAa0n7wy",
    sales_plan="1tFcx8cBSCecVoJIh4ku3z6NoZKWup47M",
    production_plan="1MbYJ2TTNnSPhcWHlRRmsxmUWKcI9BCB-",
    resource_forecast="16-3n3PhCq2VOsI9GBjMDDGvwE1Fh-MAn",
    retailers="12dHUtodZJ5Gs8QI1Rv5uXJ8ldMQCXfji",
    suppliers="1e0o3XyIsRKt3KSRfbtTW3nAnt0Jjnlwh",
    time="1SSWUFSYzo_TFkrxA_zckK7uzmSJTtSNw",
)

# https://drive.google.com/drive/folders/1p415xgKVNUbI8d5wcMVe6tP2By8EQRKK
file_ids_diaster_v1 = dict(
    finished_goods="1X83NLAXIdJAMQUKj0f3c_mwoqRQTbrQ7",
    materials="1oKFl9XJsVPFDk411lmrgZNlJQK_q39JB",
    item_types="1nmzaIxZ0_brs0n8n2yvKZ28s1yN858AE",
    items="1PhNgEKpou1Xgm7UVFhYm2hbynOpDNI2G",
    companies="1393ZnrbyMDBc__yGB6l-IDwSiguKB7-U",
    customers="1SYfsWLG4dpmgbR_NMPCKiAHBR0n69-m6",
    plants="1OkbpMus0rTjyoE2LtqWGwgs8Na7dqmaS",
    locations="1_ygUGcDOAw4Zpg89WD76ylsI_eE06L8b",
    storages="1Ld9HdIFfHbyHICFHqb_lvukpXPsspp9L",
    lines="1qry_M3k7_nI3rSEflaU4lAgoyWrjWgES",
    years="1MOLAk9pw62p55-aHv5CMq6RQPcHQhPNf",
    months="1X1l8fwSxxP3T-4LPGZ8ypuVJoeuYV1Ar",
    dates="1vcgZLcdyXnudTwvirMyvpuITgU4lX3J6",
    transactions="1eeBFOvKoNtHWtmNyGTEPV88neKLa18cI",
    transaction_types="1k5TrS6kL-L2p9xrvGNkEijaDT0fkRXec",
    bom_trees="16xMEyOq0Sq4auBNFQMiYJISYt8UJRzwX",
    sales_forecast="1FVP_zYbrgqe4wm9Wr_msYBuQIaHa2mBD",
    sales_plan="1tpvBRWleElBhSYoFugDjnnldbUF84lZV",
    production_plan="1ShFxdOHatg2Lu0xdVYZtsmylLam7qkFr",
    resource_forecast="1U4GqUWQOAOFB2W_VIyEwpA5ZG0hs4iXE",
    retailers="1RQ3R1KOSrBDvsEzYXHvLeqiJ-D4oPDqa",
    suppliers="1v_6sfhypFVH39uTxMfe3CWlYdOKXiwzl",
    time="1_x4uhwB4LKNSwZt-0syytZ0jVR1qAyqP",
)

# https://drive.google.com/drive/folders/1QLYjn-B0xcskZZ3g3C7b9lglaN768_o5
file_ids_prediction_v1_kansai_underestimation = dict(
    finished_goods="1Gt76gv83Dop3UwcAVwwDpQax2xLktT3Z",
    materials="1F8Ovn1fjewL3RTJ53sESxjAf91g99GKc",
    item_types="1mk12icSkXpxwbHmnRiAvl15lt0zSJvFj",
    items="1F2XeNfdI8gCu4kBu_BuAs1CePHOnL1lJ",
    companies="1Wxr8NuPa2Te7mskS3xBPJgtX-ISYiLVg",
    customers="1y1LDh0gnD9eaBWkr-xfwD8dAnUhh-tAt",
    plants="1qRDFLzSsZOBHE5aAfhRF2QmFKwbCTdUY",
    locations="1a6hTZQMiHKnJ84p6OI-fz75-1jJ95Hui",
    storages="18zs9X-KeHJkAjLp_tHU5cd2GmmxadCIK",
    lines="1BkHZEe8kKvo9dK0sacvoQmJlAXP3HlI3",
    years="1xMNhMtLDNlOfkx_Pr7jnKjxxlq7Xu0AY",
    months="1b0-G5thWwVc8qXSl5ArDFlWC5ePHU-Yo",
    dates="15UTu2KgGQyY8D074MNmsRtYCCCx3NFGE",
    transactions="12SKbF86-hCOmvjBsncad1wPecFK9SKrI",
    transaction_types="1hJXuW8tuAuv-jrZ_jxHZ0f4JcOdw7b9k",
    bom_trees="19ykfm5BMKkGVlDs5crnXkF5ZXrRfSvef",
    sales_forecast="1E8p_jj2iRgyEg0yms8Cm4zhwKs-KT2Ed",
    sales_plan="1LlK8l04l4eQyl7t4Y4T7iBV-DrMZ1Bt1",
    production_plan="1MZsO8NuSTEFdJj6Y8bXwsAWSza7q5qIM",
    resource_forecast="1W9UL74nGfe00GLJApCxnbGiCn2Ga768P",
    retailers="1-zxdpyOsLz5qlAJ42XMRGaQ_BjC4AyNB",
    suppliers="1vxDNt3F86BNstnkh738Ey3b-JctBCd6k",
    time="1T08IzrwqYFoy3IZf3DMVxbIdvA0yorDl",
)

datasets = dict(
    master_data_ordinary=file_ids_ordinary_v1,
    master_data_disaster=file_ids_diaster_v1,
    master_data_prediction_kansai_underestimation=file_ids_prediction_v1_kansai_underestimation,
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

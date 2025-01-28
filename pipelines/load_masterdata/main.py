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

# https://drive.google.com/drive/u/0/folders/1lpEEVOnrMSgKD0Mt1apE5C3uIymjsoLo
file_ids_ordinary_v2 = dict(
    finished_goods="1K3_fPat6m16hems_L6as1WdnQeFXJpx3",
    materials="1Phky0hm8OG5rz9rLwdKxpX7DJ4gOMT6E",
    item_types="17-UPiOvWPDv_GSl17Z6ZiHcFjIwyt_cI",
    items="10r4JXGw65f60sKkgposJuNPcbY1FObqL",
    companies="1lJkLvSiOc7NTldsBBC4iHO3dJJqoyiYs",
    customers="1OOM1Zwmi8JuvpRlclPQu9I2i6b5cj3TL",
    plants="1-2extZjWYG2iyCz3Hy4KaXKe0YDXcOpG",
    locations="1RW2LW6eTVD78nOQyP1_utkEngeR57HHZ",
    storages="1H_iyzS_NuzE5owWfAJyEcGWPVnfP8tVA",
    lines="1rrkRMVMzs97xFBXIJOw9STrgo7QlbFoc",
    years="1DaQyYjo4iEl6vb4MpbAGfoJJOsk79xbH",
    months="1oLRMQ_9qUa9plpAoxjXVxPpT19P_GkZF",
    dates="142pL3v_X-ELyEw4UjdBHy72zlSvGpngM",
    transactions="1k19XBTj5nRWSh1H7D2TFlq6aOghZaR0S",
    transaction_types="1mEeqXv4X2uNoduaIRd2ms6eav0qZ5nD3",
    bom_trees="1cShWQBvzA7Ch9yoo-519XDNAJK8MCAZ6",
    sales_forecasts="19k1MCzQKapjx-B0Vey3nbwyllxi-HroO",
    production_forecasts="1YhWBEfUop6ssYPOibwb3qs2tcMWyiUKm",
    resource_forecasts="1peF_yicUCMNhxj3B3crMy0GLUVeEY2x_",
    retailers="1m7BqYkw6IXmIPOTIGqd9x6mRyGbGrJzC",
    suppliers="1cW4ziETRpzfQC8pd2Uri1-yEI0HjfPpt",
    times="1u_1FgtTcybxf5bweuVBIHkrbZ96YnNOY",
    versions="1-HzNSLCEfRt3h9KVTcN-tKod6PiGPvnR",
    routing_forecasts="171JBG_cbqgcKbPSojv4dUpvKRZmoB0-i",
    routing="1uOOPdPLQkwc-KveEOpetnC3P1Cni9aAs",
)

# https://drive.google.com/drive/u/0/folders/1WTNpa4oZz7Vaiu4FFpkkWjYMjkBRK0sm
file_ids_diaster_v2 = dict(
    finished_goods="1yqk60S0WTlJYS6MG1K9eb-u__tSKrAmE",
    materials="1cNAXTNYpPYSdquAT5-5c1MKpc5EyJYDE",
    item_types="11AL94BNwT-Etfny5yIOSk5KVaIYFu8YL",
    items="1ITiGT8ZnK9p3O1vLE4ZaDG_yTTKbSJQ6",
    companies="1DSPem6STc-ts_ijSyTSldPgJntQrU3D1",
    customers="13BTEwQzfegfOXJVAZBmFEhv01g7G3PBd",
    plants="1y8J9kPNxgUtu_unCS9OtsKB2_ybooSrN",
    locations="18QtvztfhNiuO7NLU0cBJmUVXz_-62M2P",
    storages="1vqJ6KcR5v-NVE5f8UMVdBluulTDcuxLO",
    lines="1mDTalJNXZ_5eKf7SlvXdJLWwZkN0CG1m",
    years="1o8E7iBF2o6PuOQCSAqzgxejv-SCDBg8W",
    months="14P9fsd1HlP8BOCypcB7B-LJxVvZs30pc",
    dates="188j7-BknQRokmhIpYcQ95mn-DI9XfLhU",
    transactions="1wAuBouFxcOyUftKi2lFgH7cTitWVq_lz",
    transaction_types="1O5rN9BBXGFsAJdBIKR6S6wahQt7o0wsx",
    bom_trees="1ugj6Zcrt1z8jD58gvHuN15tAj8uMwZXB",
    sales_forecasts="1n7dMURT3Rr03rvk9UKh5Lvq5NHChpcLG",
    production_forecasts="1S_t6rzOTrT7-fkLKjaaFwQZBXHCdTEs8",
    resource_forecasts="1vLnYDMRVKp7HHf-YEbmcEhfWBjQx3AFL",
    retailers="1JINXONp_-PKk4hE_0MZk9iOSUNETvteb",
    suppliers="166k5msPMD1U8AQsWecxz8VVAf76rw1HN",
    times="1b7t5AV6xqH4POdnjb4Y5eC66CXaBLqb5",
    versions="1_sdKmQbNoZPw7Iph5l_upwgqLrQX7Gpa",
    routing_forecasts="1dOE6AoS1TAoaO2mZFmOcEBz0RWsPX4Ly",
    routing="14qpDyBfqB2BP2OaBmMoh6BeydxFM3xkv",
)

# https://drive.google.com/drive/u/0/folders/1KqFSI6PWsvU3nmarTQ0V5xWdGW4nLNHG
file_ids_prediction_kansai_v2 = dict(
    finished_goods="1dWbO1GqeVbEGZ_mDtWDq5BOZ79Npar1Z",
    materials="1oSu2z4DzF7KTaF_iVbtgrYvoo3Tz8J3Y",
    item_types="19pUSD2nB-hqOhkJYk2QLOHWwZPF9jGam",
    items="1uBCjgunRSEOqXhNsVhBEQh8v71Sj2CgD",
    companies="1LfSfaxxPbfFT8itSOUYZr_iKJyrQvOIB",
    customers="1guUD2BRhOqzAXSBjRORZoXSIRad59OeU",
    plants="10LZXg_MNvWK7r6RMRGzObCOdeO2sqtCW",
    locations="1vlSSon4B39YXqacUWYyUABWMgmgr3iCN",
    storages="1I_t4P8ykuWZ3XuqVlMj8BBi1E_2bfFxw",
    lines="1qyvFPooGD2fQ6FdlDGGAshQkle_j2kN1",
    years="1Co5NZdH_yMZvuK3WXXl8-Fyx0oaW6Y21",
    months="147L4UGz-j3biT1CqDeX1xl3nsQviA2L4",
    dates="15hHk190gY4bKbGjOPTs-PEICEj-p3ope",
    transactions="1wo9zFDbV9xOr9LlAu9xu2QqdJlBz9JEq",
    transaction_types="1UpzXCxgUbJqwfamEW5H-KEVsj8Q1hCND",
    bom_trees="1KU9HCwhplK_sJEW0v3Q1L6AwLugfhYxU",
    sales_forecasts="1rMIFuivmK-vPTMO1VrDp1zIC2MaqeKI0",
    production_forecasts="1rmEOv2tDPWxUHk-P53ZXzfQcLsAeDB3c",
    resource_forecasts="1kh-pba8sqA1dDH9zW2KQcOI8ZHMr39dd",
    retailers="19KiPBG60XuseQhaXPlbw9Ct6zEx08KPc",
    suppliers="1DVUXm_RPGdhoIScZHRm8qgDsbFzSaAX9",
    times="1_O0oSWHJFKI60oIy7D5neavsiqSt_xwh",
    versions="1yw1K31oeVbVbn32AK5eoTN8979LdIKwz",
    routing_forecasts="10J5U0dAnX9AWeVc0d2TCZT5GLzriLigg",
    routing="128zRb4KAV3-h5lJH8Pkx_VCiI44VrCQ4",
)

# https://drive.google.com/drive/u/0/folders/1-jfXdav0UHKDo28-fYthHbEx674kbsG3
file_ids_prediction_kyushu_v2 = dict(
    finished_goods="1Jvd550Jfc2yS9tubQhdI-qBZXoU0YzOs",
    materials="1ovmhSYKPlACKJh9ApfMqTsDEau8Q3eVu",
    item_types="1exXI2ZhGr1FQvMKWEGTJfwCPDz2caJJQ",
    items="1GuJVFjfP00SoIqLC55w9YiU5nNTpb3-p",
    companies="1SI4C4pVVZBiZe2fveoXjiEAAXieDF0q2",
    customers="1Tkijrm--uKawtpvA17sZYi3W-ju-qeMI",
    plants="142tUEoAUbPuu_AWxP969-yCiVZinCW3_",
    locations="1PXaBw4o1PC1VNOTx5ZQtEXAo9rZnS8Vp",
    storages="1HYjHuKkPx0R7H3sI_wadJTCElbj_ezcI",
    lines="1sDHWAeOkucGDkFuNJfmJaoMljqQfwMAG",
    years="1scpu_m5hkEyhqj5Gt6II7zTXsVgGUCt2",
    months="15o2-n8UkfDF1s1D246tUKunDEtzSnUra",
    dates="1HDxkLbpDg_MT6q5O9ssBjG9oLPFvzVkB",
    transactions="1go8q1crQ3hqQesJyfJ9DfKhd72TKYn6S",
    transaction_types="1j7TcKAOZHudKjVKxuBlHQfngPGOQzODM",
    bom_trees="1XNRe4Xv_NWK6JufhDnTeKNQpnNCB7Fjl",
    sales_forecasts="1UzSjI0T20XGGy10EoM3zqQO4HPjel49N",
    production_forecasts="1HsoNyhCqIfUykBIFFpJSckPZg1i6u981",
    resource_forecasts="1JCksxv41RKefO8H9rGZmSP1eL3qwhSF8",
    retailers="14vjWlezogdDpj3YvcJfA6uclSjYGCDnk",
    suppliers="129qKXdiT2cQ99MxHgEovTCG9lAzFQftu",
    times="14bLSiVgAXhdoFPqimQDpD_xiybeU5DrK",
    versions="1NkmbaQ2Ec9DHhZpSGBDCStEhOlDLT8ZQ",
    routing_forecasts="1Xknx1z6C-D8p-_CYt8oyABvm7nQQSjxo",
    routing="1j991-CO1snUnACnZp-GGXZHladzbroM5",
)

datasets = dict(
    master_data=file_ids_ordinary_v2,
    master_data_disaster=file_ids_diaster_v2,
    master_data_prediction_kansai=file_ids_prediction_kansai_v2,
    master_data_prediction_kyushu=file_ids_prediction_kyushu_v2,
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

import json
import os
from typing import Tuple
import zipfile
import requests
import geopandas as gpd
import firebase_admin
import boto3
from firebase_admin import credentials, messaging
from botocore.exceptions import ClientError

# default_app = firebase_admin.initialize_app()
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


def get_secret():
    secret_name = "firebase_creds"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(get_secret_value_response["SecretString"])
        firebase_creds = json.loads(secret["firebase_creds"])
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    return firebase_creds


cred = credentials.Certificate(get_secret())
firebase_admin.initialize_app(cred)


def get_spc_day(day, extract_dir: str = "/tmp/shapefiles"):
    base_url = "https://www.spc.noaa.gov/products/outlook/"
    directory = "/tmp"
    day_file = f"day{day}otlk-shp.zip"

    url = base_url + day_file
    file_name = os.path.join(directory, day_file)

    result = requests.get(url)

    if result.status_code == 200:
        # Save the content to a file
        with open(file_name, "wb") as f:
            f.write(result.content)
        print("File downloaded successfully.")
    else:
        print(f"url: {url}")
        print(f"result.status_code: {result.status_code}")
        print(f"result.text: {result.text}")
        raise Exception("Failed to download the file.")

    with zipfile.ZipFile(file_name, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
        print("File extracted successfully.")

    os.remove(file_name)
    print("Cleanup complete: Removed downloaded zip file.")

    return extract_dir


def load_day(day, extract_dir: str = "/tmp/shapefiles"):
    filepath = os.path.join(extract_dir, f"day{day}otlk_cat.shp")
    gdf = gpd.read_file(filepath)
    print(f"Shapefile day1otlk_cat loaded successfully.")

    return gdf


def check_loc_in_outlook(gdf: gpd.GeoDataFrame, lon: float, lat: float):
    # show column headers of gdf
    print(gdf)
    # coordinates of Tulsa
    # check if is in the multipolygons in teh geometry field of each gdf row
    relevant_label = None
    for idx, row in gdf.iterrows():
        try:
            relevant_label = row["LABEL"]
        except KeyError:
            continue
        print(f"relevant_label: {idx}, {relevant_label}")
        print(f"city_coords: {(lon, lat)}")
        if row["geometry"].contains(gpd.points_from_xy([lon], [lat])[0]):
            print(f"Found Tulsa in outlook: {relevant_label}")
            return relevant_label

    return None


def build_message(
    risk_label: str,
    token: str = "ew6m3kNBQvK_C-g3HUOS6k:APA91bHnhFW-r9Ioz_7FgxIiHhn2EC5HZvBYD3OcbyfBStrYbD6SXDVSjtYye1SX7um1rTM2W5pJj8cyvzY5Nn6fWmb-B8uk2t2DauDoy8H6atLQfAUzlxE",
):
    body = "No Storm Prediction Center risk in your area today"
    if risk_label:
        body = f"{risk_label} is the Storm Prediction Center risk today"

    message = messaging.Message(
        notification=messaging.Notification(
            title="SPC Checker",
            body=body,
        ),
        token=token,
    )
    return message


def send_notification(message: messaging.Message):
    response = messaging.send(message)
    print(f"response: {response}")
    return response

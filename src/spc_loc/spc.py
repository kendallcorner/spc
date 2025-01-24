from collections import OrderedDict
import os
import zipfile
import requests
import geopandas as gpd
import firebase_admin
from firebase_admin import credentials, messaging

# default_app = firebase_admin.initialize_app()
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

cred = credentials.Certificate(creds)

firebase_admin.initialize_app(cred)


def get_spc_day_1(day: int = 1, extract_dir: str = "/tmp/shapefiles"):
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


def load_day_1(day: int = 1, extract_dir: str = "/tmp/shapefiles"):
    filepath = os.path.join(extract_dir, f"day{day}otlk_cat.shp")
    gdf = gpd.read_file(filepath)
    print(f"Shapefile day1otlk_cat loaded successfully.")

    return gdf


def check_loc_in_outlook(gdf: gpd.GeoDataFrame):
    # show column headers of gdf
    print(gdf)
    # coordinates of Tulsa
    tulsa = (-95.9928, 36.1540)
    # check if is in the multipolygons in teh geometry field of each gdf row
    relevant_label = None
    for idx, row in gdf.iterrows():
        if row["geometry"].contains(gpd.points_from_xy([tulsa[0]], [tulsa[1]])[0]):
            print(f"Found Tulsa in outlook: {row['LABEL']}")
            relevant_label = row["LABEL"]
    return relevant_label


def send_notification(
    description: str,
    token: str = "ew6m3kNBQvK_C-g3HUOS6k:APA91bHnhFW-r9Ioz_7FgxIiHhn2EC5HZvBYD3OcbyfBStrYbD6SXDVSjtYye1SX7um1rTM2W5pJj8cyvzY5Nn6fWmb-B8uk2t2DauDoy8H6atLQfAUzlxE",
):
    """Send a push notification to a specific device using FCM.

    Args:
        token (str): The FCM token of the target device.
        title (str): Title of the notification.
        body (str): Body text of the notification.

    Returns:
        str: Message ID of the sent notification.
    """
    # Create a message object
    message = messaging.Message(
        notification=messaging.Notification(
            title="SPC Checker",
            body=f"The Storm Prediction Center risk in Tulsa today is {description}",
        ),
        token=token,
    )
    response = messaging.send(message)
    print(f"response: {response}")
    return response

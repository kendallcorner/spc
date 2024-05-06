from collections import OrderedDict
from datetime import date
import os
import zipfile
import requests
import geopandas as gpd
from twilio.rest import Client


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


def send_text_message(label):

    labels = OrderedDict(
        {
            "TSTM": "Thunderstorm",
            "MRGL": "Marginal Risk",
            "SLGT": "Slight Risk",
            "ENH": "Enhanced Risk",
            "MDT": "Moderate Risk",
            "HIGH": "High Risk",
        }
    )
    description = labels.get(label)
    if description:
        print(f"Sending text message: {description}")
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_="+18339876891",
            body=f"The Storm Prediction Center risk in Tulsa today is {description}",
            to="+19186401377",
        )
        print(message.sid)
    else:
        print("No elevated risk to send.")


if __name__ == "__main__":
    get_spc_day_1()
    gdf = load_day_1()
    label = check_loc_in_outlook(gdf)
    send_text_message(label)

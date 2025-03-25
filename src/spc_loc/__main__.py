import os
import json
import requests
from spc_loc.db import get_phones_list
from spc_loc.spc import (
    build_message,
    get_spc_day,
    load_day,
    check_loc_in_outlook,
    send_notification,
)


def run_main(event, context):
    day = 1
    get_spc_day(day=day)
    gdf = load_day(day=day)
    phones_list = [
        {
            "phone_id": "",
            "fcm_token": "ew6m3kNBQvK_C-g3HUOS6k:APA91bHnhFW-r9Ioz_7FgxIiHhn2EC5HZvBYD3OcbyfBStrYbD6SXDVSjtYye1SX7um1rTM2W5pJj8cyvzY5Nn6fWmb-B8uk2t2DauDoy8H6atLQfAUzlxE",
            "lat": 36.1540,
            "lon": -95.9928,
        }
    ]
    phones_list = get_phones_list()
    results = []
    for app_data in phones_list:
        lon = app_data["lon"]
        lat = app_data["lat"]
        phone_id = app_data["phone_id"]
        fcm_token = app_data["fcm_token"]

        label = check_loc_in_outlook(gdf, lon, lat)
        message = build_message(label, token=fcm_token)
        response = send_notification(message)
        results.append({"phone_id": phone_id, "response": response})

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": "Successfully processed SPC data", "results": results}
        ),
    }


def lambda_handler():
    # Get next event from Lambda Runtime API
    runtime_api = os.environ.get("AWS_LAMBDA_RUNTIME_API")
    next_invocation_url = f"http://{runtime_api}/2018-06-01/runtime/invocation/next"

    response = requests.get(next_invocation_url)
    request_id = response.headers.get("Lambda-Runtime-Aws-Request-Id")

    # Process the event
    try:
        # We don't currently use event
        event = json.loads(response.content) if response.content else {}
        result = run_main(event, None)

        # Send the response back
        response_url = (
            f"http://{runtime_api}/2018-06-01/runtime/invocation/{request_id}/response"
        )
        requests.post(response_url, json=result)
    except Exception as e:
        # Send error response if something goes wrong
        error_url = (
            f"http://{runtime_api}/2018-06-01/runtime/invocation/{request_id}/error"
        )
        error_payload = {"errorMessage": str(e), "errorType": type(e).__name__}
        requests.post(error_url, json=error_payload)


if __name__ == "__main__":
    # Check if running in Lambda environment
    if os.environ.get("AWS_LAMBDA_RUNTIME_API"):
        lambda_handler()
    else:
        # Running locally
        result = run_main(None, None)
        print(f"Local execution completed with result: {result}")

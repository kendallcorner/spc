import os
import json
import requests
from spc_loc.spc import (
    build_message,
    get_spc_day,
    load_day,
    check_loc_in_outlook,
    send_notification,
)


def run_main(event, context):
    day = 2
    get_spc_day(day=day)
    gdf = load_day(day=day)
    cities = {"Tulsa": (-95.9928, 36.1540)}
    results = []
    for city_name, city_coords in cities.items():
        label = check_loc_in_outlook(gdf, city_coords)
        message = build_message(label, city_name)
        response = send_notification(message)
        results.append({"city": city_name, "response": response})

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

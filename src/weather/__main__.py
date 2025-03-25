import json
import os

import requests


def run_main(event, context):
    url = "https://api.weather.gov/gridpoints/TSA/41,105/forecast/hourly"
    response = requests.get(url)
    data = response.json()
    forecast = data["properties"]["periods"]
    temps = [(i, period["temperature"]) for i, period in enumerate(forecast)]
    str_temps_list = [
        f"{(i - 8) / 21 * 200},{temp / 50 * 150}"
        for i, temp in temps
        if i < 30 and i > 8
    ]
    print(f"Temps: {' '.join(str_temps_list)}")
    return None


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

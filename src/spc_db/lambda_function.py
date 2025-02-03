import base64
from decimal import Decimal
import json
import boto3
from datetime import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("SPC_app")  # Replace with your table name


def float_to_decimal(float_value):
    """Convert a float to a Decimal with proper rounding."""
    return Decimal(str(round(float(float_value), 6)))


def lambda_handler(event, context):
    print(f"event: {event}")
    # try:
    # Parse the request body
    if event["isBase64Encoded"]:
        decoded_body = base64.b64decode(event["body"]).decode("utf-8")
    else:
        decoded_body = event["body"]
    body = json.loads(decoded_body)
    print(f"body: {body}")

    # Validate required field
    if "phone_id" not in body:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "phone_id is required"}),
        }

    # Prepare item for DynamoDB
    item = {
        "phone_id": body["phone_id"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    # Add optional fields if they exist
    if "fcm_token" in body:
        item["fcm_token"] = body["fcm_token"]
    if "lat" in body:
        item["lat"] = float_to_decimal(body["lat"])
    if "lon" in body:
        item["lon"] = float_to_decimal(body["lon"])

    print(f"item: {item}")
    # Insert into DynamoDB
    table.put_item(Item=item)

    return {
        "statusCode": 201,
        "body": json.dumps(
            {
                "phone_id": item["phone_id"],
                "created_at": item["created_at"],
            }
        ),
    }

    # except json.JSONDecodeError:
    #     return {
    #         "statusCode": 400,
    #         "body": json.dumps({"error": "Invalid JSON in request body"}),
    #     }
    # except Exception as e:
    #     return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

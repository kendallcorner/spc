import base64
from decimal import Decimal
import json
import os
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
    headers = event["headers"]
    api_key = headers["authorization"]
    if api_key != os.getenv("SPC_DB_API_KEY"):
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorized"}),
        }
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

    # Start building update expression
    update_expression = ["updated_at = :updated_at"]
    expression_values = {
        ":updated_at": datetime.now().isoformat(),
    }

    # Check if this is a new item
    try:
        response = table.get_item(Key={"phone_id": body["phone_id"]})
        is_new_item = "Item" not in response
    except Exception:
        is_new_item = True

    if is_new_item:
        update_expression.append("created_at = :created_at")
        expression_values[":created_at"] = datetime.now().isoformat()

    # Add optional fields if they exist
    if "fcm_token" in body:
        update_expression.append("fcm_token = :fcm_token")
        expression_values[":fcm_token"] = body["fcm_token"]

    if "lat" in body and body["lat"] is not None:
        update_expression.append("lat = :lat")
        expression_values[":lat"] = float_to_decimal(body["lat"])

    if "lon" in body and body["lon"] is not None:
        update_expression.append("lon = :lon")
        expression_values[":lon"] = float_to_decimal(body["lon"])

    # Update DynamoDB
    update_expr = "SET " + ", ".join(update_expression)
    table.update_item(
        Key={"phone_id": body["phone_id"]},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expression_values,
    )

    return {
        "statusCode": 201,
        "body": json.dumps(
            {
                "phone_id": body["phone_id"],
                "updated_at": expression_values[":updated_at"],
            }
        ),
    }

import boto3


def get_phones_list():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("SPC_app")
    response = table.scan()
    phones_list = response["Items"]
    print(f"phones_list: {phones_list}")
    return phones_list

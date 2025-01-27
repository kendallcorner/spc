from spc_loc.spc import (
    get_spc_day_1,
    load_day_1,
    check_loc_in_outlook,
    send_notification,
)


def lambda_handler(event, context):
    get_spc_day_1()
    gdf = load_day_1()
    label = check_loc_in_outlook(gdf)
    send_notification(label)
    return {"statusCode": 200, "body": "Success!"}


if __name__ == "__main__":
    lambda_handler(None, None)

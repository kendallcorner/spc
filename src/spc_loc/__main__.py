from spc_loc.spc import (
    build_message,
    get_spc_day,
    load_day,
    check_loc_in_outlook,
    send_notification,
)


def lambda_handler(event, context):
    day = 2
    get_spc_day(day=day)
    gdf = load_day(day=day)
    cities = {"Tulsa": (-95.9928, 36.1540)}
    for city_name, city_coords in cities.items():
        label = check_loc_in_outlook(gdf, city_coords)
        message = build_message(label, city_name)
        send_notification(message)
    exit(0)


if __name__ == "__main__":
    lambda_handler(None, None)

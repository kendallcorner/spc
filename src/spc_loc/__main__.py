from spc_loc.spc import (
    get_spc_day_1,
    load_day_1,
    check_loc_in_outlook,
    send_notification,
)

if __name__ == "__main__":
    get_spc_day_1()
    gdf = load_day_1()
    label = check_loc_in_outlook(gdf)
    send_notification(label)

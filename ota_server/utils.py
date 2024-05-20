def print_devices(devices):
    print(
        f"{'MAC':<20} {'FW Version':<15} {'Update Time':<20} " f"{'Last Seen Time':<20}"
    )
    print("=" * 75)
    for mac, info in devices.items():
        update_time = (
            info["Update Time"].strftime("%Y-%m-%d %H:%M:%S")
            if info["Update Time"]
            else "N/A"
        )
        last_seen_time = info["Last Seen Time"].strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"{mac:<20} {info['FW Version']:<15} {update_time:<20} "
            f"{last_seen_time:<20}"
        )
    print()


def print_google_spreadsheet_dict(report):
    data = []
    for info in report:
        data.append(
            {
                "MAC": info["MAC"],
                "FW Version": info["FW Version"],
                "Update Time": (
                    info["Update Time"].strftime("%Y-%m-%d %H:%M:%S")
                    if info["Update Time"]
                    else "N/A"
                ),
                "Last Seen Time": info["Last Seen Time"].strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    print("Google Spreadsheet Data:")
    print(data)
    print()

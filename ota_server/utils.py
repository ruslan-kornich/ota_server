import logging
import re


def table_log_devices(devices):
    logging.info(
        f"{'MAC':<20} {'FW Version':<15} {'Update Time':<20} {'Last Seen Time':<20}"
    )
    logging.info("=" * 75)
    for mac, info in devices.items():
        update_time = (
            info["Update Time"].strftime("%Y-%m-%d %H:%M:%S")
            if info["Update Time"]
            else "N/A"
        )
        last_seen_time = info["Last Seen Time"].strftime("%Y-%m-%d %H:%M:%S")
        logging.info(
            f"{mac:<20} {info['FW Version']:<15} {update_time:<20} {last_seen_time:<20}"
        )


def send_data_to_google_spreadsheet(report):
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
    logging.info("Google Spreadsheet Data:")
    for entry in data:
        logging.info(entry)


def is_valid_mac(mac):
    return re.match("[0-9a-f]{2}([:-][0-9a-f]{2}){5}$", mac.lower())

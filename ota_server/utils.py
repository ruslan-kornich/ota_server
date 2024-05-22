import logging
import re


def send_data_to_google_spreadsheet(report):
    logging.info("Google Spreadsheet Data:")
    for info in report:
        data = {
            "MAC": info["MAC"],
            "FW Version": info["FW Version"],
            "Update Time": (
                info["Update Time"].strftime("%Y-%m-%d %H:%M:%S")
                if info["Update Time"]
                else "N/A"
            ),
            "Last Seen Time": info["Last Seen Time"].strftime("%Y-%m-%d %H:%M:%S"),
        }
        logging.info(data)


def is_valid_mac(mac):
    return re.match("[0-9a-f]{2}([:-][0-9a-f]{2}){5}$", mac.lower())

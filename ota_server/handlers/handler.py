from http.server import BaseHTTPRequestHandler
import datetime
import os
import re
import logging
from ota_server.utils import (
    table_log_devices,
    send_data_to_google_spreadsheet,
    is_valid_mac,
)

VERSION_FILE_PATH = "ota_server/version/version.txt"
FIRMWARE_DIR_PATH = "ota_server/firmware"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class OTARequestHandler(BaseHTTPRequestHandler):
    devices = {}

    def do_GET(self):
        mac_address = self.headers.get("_br_mac_")
        firmware_version = self.headers.get("_br_fwv_")

        if not mac_address or not firmware_version or not is_valid_mac(mac_address):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"Unauthorized")
            logging.warning(
                f"Unauthorized access attempt with MAC: {mac_address}, FW Version: {firmware_version}"
            )
            return

        now = datetime.datetime.utcnow()

        if self.path == "/version.txt":
            self.handle_version_txt(mac_address, firmware_version, now)
        elif self.path == "/firmware.bin":
            self.handle_firmware_bin(mac_address, firmware_version, now)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            logging.warning(f"404 Not Found: {self.path}")

    def handle_version_txt(self, mac_address, firmware_version, now):
        new_or_updated = False

        if mac_address not in self.devices:
            self.devices[mac_address] = {
                "MAC": mac_address,
                "FW Version": firmware_version,
                "Last Seen Time": now,
                "Update Time": None,
            }
            logging.info(f"New device added: {mac_address}")
            new_or_updated = True
        else:
            self.devices[mac_address]["Last Seen Time"] = now
            if self.devices[mac_address]["FW Version"] != firmware_version:
                self.devices[mac_address]["Update Time"] = now
                self.devices[mac_address]["FW Version"] = firmware_version
                logging.info(
                    f"Device firmware updated: {mac_address} to version {firmware_version}"
                )
                new_or_updated = True

        # table_log_devices(self.devices)
        if new_or_updated:
            send_data_to_google_spreadsheet([self.devices[mac_address]])
        self.send_response(200)
        self.end_headers()
        try:
            with open(VERSION_FILE_PATH, "rb") as file:
                self.wfile.write(file.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")
            logging.error(f"Error reading version file: {e}")

    def handle_firmware_bin(self, mac_address, firmware_version, now):
        new_or_updated = False
        latest_firmware_version = self.get_latest_firmware_version()
        firmware_file = os.path.join(
            FIRMWARE_DIR_PATH, f"firmware_{firmware_version}.bin"
        )

        if not os.path.exists(firmware_file):
            logging.error(
                f"Requested firmware version {firmware_version} not found for device {mac_address}."
            )
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Firmware version not found.")
            return

        if mac_address in self.devices:
            current_version = self.devices[mac_address]["FW Version"]
            if firmware_version == current_version:
                self.devices[mac_address]["Last Seen Time"] = now
                # table_log_devices(self.devices)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(
                    f"You are already on version {firmware_version}. "
                    f"Latest available version is {latest_firmware_version}.".encode()
                )
                logging.info(
                    f"Device {mac_address} checked for firmware version {firmware_version}, already up-to-date."
                )
                return
            else:
                self.devices[mac_address]["Update Time"] = now
                self.devices[mac_address]["FW Version"] = firmware_version
                if firmware_version < current_version:
                    logging.info(
                        f"Device {mac_address} downgraded from version {current_version} to {firmware_version}."
                    )
                else:
                    logging.info(
                        f"Device {mac_address} upgraded from version {current_version} to {firmware_version}."
                    )
                new_or_updated = True

        # table_log_devices(self.devices)
        if new_or_updated:
            send_data_to_google_spreadsheet([self.devices[mac_address]])
        self.send_response(200)
        self.end_headers()
        try:
            with open(firmware_file, "rb") as file:
                self.wfile.write(file.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")
            logging.error(f"Error reading firmware file: {e}")

    @staticmethod
    def get_latest_firmware_version():
        try:
            with open(VERSION_FILE_PATH, "r") as file:
                return file.read().strip()
        except Exception as e:
            logging.error(f"Error reading latest firmware version file: {e}")
            return "unknown"

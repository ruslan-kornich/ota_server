from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from http.server import HTTPServer
import datetime
import os
from .utils import print_devices, print_google_spreadsheet_dict

VERSION_FILE_PATH = "ota_server/version/version.txt"
FIRMWARE_DIR_PATH = "ota_server/firmware"


class OTARequestHandler(BaseHTTPRequestHandler):
    devices = {}

    def do_GET(self):
        if not self.headers.get("_br_mac_") or not self.headers.get("_br_fwv_"):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"Unauthorized")
            return

        mac_address = self.headers["_br_mac_"]
        firmware_version = self.headers["_br_fwv_"]
        now = datetime.datetime.utcnow()

        if self.path == "/version.txt":
            self.handle_version_txt(mac_address, firmware_version, now)
        elif self.path == "/firmware.bin":
            self.handle_firmware_bin(mac_address, firmware_version, now)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def handle_version_txt(self, mac_address, firmware_version, now):
        new_or_updated = False

        if mac_address not in self.devices:
            self.devices[mac_address] = {
                "MAC": mac_address,
                "FW Version": firmware_version,
                "Last Seen Time": now,
                "Update Time": None,
            }
            print("New device added:")
            new_or_updated = True
        else:
            self.devices[mac_address]["Last Seen Time"] = now
            if self.devices[mac_address]["FW Version"] != firmware_version:
                self.devices[mac_address]["Update Time"] = now
                self.devices[mac_address]["FW Version"] = firmware_version
                print("Device firmware updated:")
                new_or_updated = True

        print_devices(self.devices)
        if new_or_updated:
            print_google_spreadsheet_dict([self.devices[mac_address]])
        self.send_response(200)
        self.end_headers()
        with open(VERSION_FILE_PATH, "rb") as file:
            self.wfile.write(file.read())

    def handle_firmware_bin(self, mac_address, firmware_version, now):
        new_or_updated = False
        latest_firmware_version = self.get_latest_firmware_version()
        firmware_file = os.path.join(
            FIRMWARE_DIR_PATH, f"firmware_{firmware_version}.bin"
        )

        if not os.path.exists(firmware_file):
            print(
                f"Error: Requested firmware version {firmware_version} "
                f"not found for device {mac_address}."
            )
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Firmware version not found.")
            return

        if mac_address in self.devices:
            current_version = self.devices[mac_address]["FW Version"]
            if firmware_version == current_version:
                self.devices[mac_address]["Last Seen Time"] = now
                print_devices(self.devices)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(
                    f"You are already on version {firmware_version}. "
                    f"Latest available version is {latest_firmware_version}.".encode()
                )
                return
            else:
                self.devices[mac_address]["Update Time"] = now
                self.devices[mac_address]["FW Version"] = firmware_version
                if firmware_version < current_version:
                    print(
                        f"Device {mac_address} downgraded from version "
                        f"{current_version} to {firmware_version}."
                    )
                else:
                    print(
                        f"Device {mac_address} upgraded from version "
                        f"{current_version} to {firmware_version}."
                    )
                new_or_updated = True

        print_devices(self.devices)
        if new_or_updated:
            print_google_spreadsheet_dict([self.devices[mac_address]])
        self.send_response(200)
        self.end_headers()
        with open(firmware_file, "rb") as file:
            self.wfile.write(file.read())

    def get_latest_firmware_version(self):
        with open(VERSION_FILE_PATH, "r") as file:
            return file.read().strip()


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def run(server_class=ThreadingHTTPServer, handler_class=OTARequestHandler, port=7777):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting OTA server on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()

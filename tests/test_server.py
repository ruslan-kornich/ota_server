import unittest
import os
from http.server import HTTPServer
from ota_server.server import OTARequestHandler, run
import threading
import requests

SERVER_PORT = 7777
BASE_URL = f"http://localhost:{SERVER_PORT}"


class TestOTARequestHandler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("localhost", SERVER_PORT), OTARequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_version_txt_without_headers(self):
        response = requests.get(f"{BASE_URL}/version.txt")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.text, "Unauthorized")

    def test_firmware_bin_without_headers(self):
        response = requests.get(f"{BASE_URL}/firmware.bin")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.text, "Unauthorized")

    def test_version_txt_with_headers(self):
        headers = {"_br_mac_": "00:11:22:33:44:55", "_br_fwv_": "1.0.0"}
        response = requests.get(f"{BASE_URL}/version.txt", headers=headers)
        self.assertEqual(response.status_code, 200)
        with open("ota_server/version/version.txt", "rb") as file:
            self.assertEqual(response.content, file.read())

    def test_firmware_bin_with_headers(self):
        headers = {"_br_mac_": "00:11:22:33:44:55", "_br_fwv_": "1.0.0"}
        firmware_version = "1.0.0"
        firmware_file_path = f"ota_server/firmware/firmware_{firmware_version}.bin"
        with open(firmware_file_path, "wb") as file:
            file.write(b"Fake firmware content")

        response = requests.get(f"{BASE_URL}/firmware.bin", headers=headers)
        self.assertEqual(response.status_code, 200)
        with open(firmware_file_path, "rb") as file:
            self.assertEqual(response.content, file.read())


        os.remove(firmware_file_path)

    def test_version_txt_with_different_firmware_version(self):
        headers = {"_br_mac_": "00:11:22:33:44:55", "_br_fwv_": "1.0.0"}
        response = requests.get(f"{BASE_URL}/version.txt", headers=headers)
        self.assertEqual(response.status_code, 200)

        headers["_br_fwv_"] = "2.0.0"
        response = requests.get(f"{BASE_URL}/version.txt", headers=headers)
        self.assertEqual(response.status_code, 200)
        with open("ota_server/version/version.txt", "rb") as file:
            self.assertEqual(response.content, file.read())

    def test_firmware_bin_version_not_found(self):
        headers = {"_br_mac_": "00:11:22:33:44:55", "_br_fwv_": "nonexistent_version"}
        response = requests.get(f"{BASE_URL}/firmware.bin", headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.text, "Firmware version not found.")


if __name__ == "__main__":
    unittest.main()

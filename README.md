# OTA Server

This is a simple HTTP server used for OTA updates for devices. The server logs the following information:
- Last Seen Time
- Update Time
- Current Firmware Version
- Device MAC address

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ruslan-kornich/ota_server.git
   cd ota_server
   ```
   
2. **Create and activate a virtual environment:**:
```bash
    python -m venv venv
    source venv/bin/activate  

   ```



3. **Install dependencies:**:

 ```bash
   pip install -r requirements.txt 

   ```
# Running the Server

To start the server, run the following command:
```bash
   python -m ota_server.server

   ```
The server will start on port 7777 by default.
# Testing the Server

## Check Firmware Version

To check the firmware version, use the following curl command:

```bash
   curl -X GET http://localhost:7777/version.txt \
     -H 'cache-control: no-cache' \
     -H 'Connection: close' \
     -H '_br_mac_: 00:11:22:33:44:55' \
     -H '_br_fwv_: v1.0.0'


   ```
This request should return the contents of the version.txt file.

## Download Firmware

To download the firmware, use the following curl command:
```bash
   curl -X GET http://localhost:7777/firmware.bin \
     -H 'cache-control: no-cache' \
     -H 'Connection: close' \
     -H '_br_mac_: 00:11:22:33:44:55' \
     -H '_br_fwv_: v1.0.0'
   ```
This request should return the contents of the firmware_<version>.bin file.

# File Locations

- Version File: ota_server/version/version.txt
- Firmware Files: ota_server/firmware/firmware_<version>.bin

Ensure these files exist in their respective directories for the server to function correctly.

# Logging
The server logs information about each device's interaction:

- Last Seen Time: When the device last checked the firmware version.
- Update Time: When the device last updated its firmware.
- Current Firmware Version: The current firmware version of the device.
- MAC: The MAC address of the device.

# Handling Signals
The server handles shutdown signals (e.g., SIGINT for Ctrl+C) gracefully, ensuring all threads are properly terminated.


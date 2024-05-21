import signal
import threading
import argparse
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from .handlers.handler import OTARequestHandler
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def run(server_class=ThreadingHTTPServer, handler_class=OTARequestHandler, port=7777):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Starting OTA server on port {port}...")

    def signal_handler(sig, frame):
        logging.info("Shutting down server...")
        threading.Thread(target=httpd.shutdown).start()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        httpd.serve_forever()
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        logging.info("Server successfully shut down.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start OTA server.")
    parser.add_argument(
        "--port",
        type=int,
        default=7777,
        help="Port number to run the server on (default: 7777)",
    )
    args = parser.parse_args()
    run(port=args.port)

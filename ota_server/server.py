import signal
import threading
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from .handlers.handler import OTARequestHandler


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def run(server_class=ThreadingHTTPServer, handler_class=OTARequestHandler, port=7777):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting OTA server on port {port}...")

    def signal_handler(sig, frame):
        print("Shutting down server...")
        threading.Thread(target=httpd.shutdown).start()

    signal.signal(signal.SIGINT, signal_handler)

    httpd.serve_forever()
    print("Server successfully shut down.")


if __name__ == "__main__":
    run()

from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime

devices = {}


class RequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, status=200, content_type="text/plain"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        mac = self.headers.get('_br_mac_')
        fwv = self.headers.get('_br_fwv_')

        if not mac or not fwv:
            self._set_response(400)
            self.wfile.write(b'Missing custom headers')
            return

        current_time = datetime.datetime.utcnow()

        if mac not in devices:
            devices[mac] = {
                'fwv': fwv,
                'last_seen': current_time,
                'update_time': None
            }
            # Trigger signal for new device info
        else:
            if devices[mac]['fwv'] != fwv:
                devices[mac]['fwv'] = fwv
                devices[mac]['update_time'] = current_time
                # Trigger signal for firmware version change
            devices[mac]['last_seen'] = current_time

        if self.path == '/version.txt':
            self._set_response()
            self.wfile.write(b'v1.0.0')
        elif self.path == '/firmware.bin':
            self._set_response(content_type='application/octet-stream')
            with open('ota_server/firmware/firmware.bin', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self._set_response(404)
            self.wfile.write(b'Not Found')


def run(server_class=HTTPServer, handler_class=RequestHandler, port=777):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}')
    httpd.serve_forever()


if __name__ == "__main__":
    run()

import time
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import re
import logging
from .manager import StubManager


def build_stub_manager(stub_manager):

    class StubManagerServer(BaseHTTPRequestHandler):

        def _set_success(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()

        def _set_bad_request(self):
            self.send_response(400)
            self.end_headers()

        def do_GET(self):
            param = "consumer"
            if re.search(f'/stub\?{param}=\w+', self.path):
                logging.info(f"Request: GET {self.path}\nHeaders:\n{self.headers}\n")
                params = parse_qs(urlparse(self.path).query)
                consumer = params[param][0]
                stub_manager.start(consumer)
                time.sleep(8)
                self._set_success()
                self.wfile.write(f"{consumer} stub consumer requested".encode('utf-8'))
            else:
                logging.error("stub consumer parameter has not been provided")
                self._set_bad_request()

    return StubManagerServer


def run(port=8080, consumer=None):
    logging.basicConfig(level=logging.INFO)
    stub_manager = None
    try:
        logging.info('Starting stubrunner...\n')
        stub_manager = StubManager(port, consumer)

        logging.info('Starting httpd...\n')
        httpd = HTTPServer(('', port), build_stub_manager(stub_manager))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        logging.info('Stopping httpd...\n')
        httpd.server_close()
    except OSError:
        logging.error('httpd start has failed.\n')
        traceback.print_exc()
    finally:
        logging.info('Stopping stubrunner...\n')
        stub_manager.terminate()

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Thread

from f3d_extras.files import download_file_if_url


def test_download_file_if_url_with_file():
    with NamedTemporaryFile() as tmp:
        tmp.write(b"lorem ipsum")
        tmp.flush()

        assert download_file_if_url(tmp.name) == Path(tmp.name)
        assert download_file_if_url(Path(tmp.name)) == Path(tmp.name)


def test_download_file_if_url_with_url():
    RESPONSE_TEXT = b"lorem ipsum"

    class HTTPRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(RESPONSE_TEXT)
            self.wfile.close()

    httpd = HTTPServer(("", 0), HTTPRequestHandler)
    thread = Thread(target=httpd.serve_forever)
    thread.start()

    downloaded = download_file_if_url(f"http://localhost:{httpd.server_port}/whatever.xyz?hello=world")
    assert downloaded.name.endswith(".xyz")
    assert Path(downloaded).read_bytes() == RESPONSE_TEXT

    httpd.shutdown()
    thread.join()

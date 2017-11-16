# Serves Talky and related data
# TODO

from http.server import BaseHTTPRequestHandler, HTTPServer
import base64
from pathlib import Path
import json

import tkinter as tk

key = base64.b64encode(b"admin:1234").decode("ascii")
save_dir = Path("../tests")
game_dir = Path("../gamedata")

class TalkitRequestHandler(BaseHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", "Basic realm=\"Enter a nickname and (unique) password for this session. Then, accept them in server UI.\"")
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        global key
        if self.headers.get("Authorization") == None:
            self.do_AUTHHEAD()
        elif self.headers.get("Authorization") == "Basic " + key:
            self.send_response(200)
            data_file = self.path
            if data_file == "/":
                data_file = "index.html"

            content_type = "text/html"
            if data_file.endswith(".css"):
                content_type = "text/css"
            elif data_file.endswith(".js"):
                content_type = "text/javascript"
            elif data_file.endswith(".json"):
                content_type = "application/json"
            self.send_header("Content-type", content_type + "; charset=utf-8")
            self.end_headers()

            if data_file == "/saves.json":
                self.get_saves()
                return
            if data_file.startswith("/saves/"):
                self.wfile.write(Path(save_dir, data_file.split("/")[2]).read_bytes())
                return

            self.wfile.write(Path("../" + data_file).read_bytes())
        else:
            self.do_AUTHHEAD()
            self.wfile.write(bytes("incorrect", "utf-8"))

    def get_saves(self):
        global save_dir
        response = []
        for f in save_dir.iterdir():
            response.append(f.name)
        self.wfile.write(bytes(json.dumps(response), "utf-8"))

    def do_POST(self):
        global key
        if self.headers.get("Authorization") == "Basic " + key:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            if self.path == "/delete_story":
                Path(save_dir, post_data.decode("utf-8")).unlink()
                Path(game_dir, post_data.decode("utf-8")).unlink() # Delete gamedata too
            if self.path.startswith("/save_story"):
                Path(save_dir, self.path.split(":")[1]).write_bytes(post_data)
            if self.path.startswith("/save_gamedata"):
                Path(game_dir, self.path.split(":")[1]).write_bytes(post_data)

            self.send_response(200)

def run_server():
    server_address = ("127.0.0.1", 8081)
    httpd = HTTPServer(server_address, TalkitRequestHandler)
    httpd.serve_forever()

run_server()

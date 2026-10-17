import json
import logging
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

import psycopg
from psycopg.rows import dict_row

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def get_connection():
    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        sslmode=os.environ.get("PGSSLMODE", "require"),
        connect_timeout=5,
        row_factory=dict_row,
    )


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/health":
            self.respond(200, {
                "status": "healthy",
                "service": "devops-backend",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        elif path == "/api/tasks":
            try:
                with get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT id, name, completed FROM tasks ORDER BY id")
                        tasks = cursor.fetchall()
                self.respond(200, {"tasks": tasks})
            except psycopg.Error:
                logging.exception("Database query failed")
                self.respond(503, {"error": "Database temporarily unavailable"})
        else:
            self.respond(404, {"error": "Not found"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 3000), Handler)
    print("API listening on port 3000", flush=True)
    server.serve_forever()

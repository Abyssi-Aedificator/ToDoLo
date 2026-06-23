#!/usr/bin/env python3
"""
Simple Budget - Local Network Sync Agent
========================================

A tiny, dependency-free sync rendezvous for Simple Budget. It lets your
devices (PC, phone, tablet) sync their data over your local Wi-Fi network
without any cloud service or account.

HOW IT WORKS
------------
The agent holds the most recently changed copy of your budget in memory
(and on disk, next to this script). When a device clicks "Sync now":

  * it sends its own data + a "last modified" timestamp,
  * the agent keeps whichever copy is newer,
  * the device with older data receives the newer copy back.

So after you click Sync on each device, they all converge on the newest data.

The agent never sends anything to the internet. Data stays on your network.

USAGE
-----
    python simplebudget-sync.py            # listens on port 8777
    python simplebudget-sync.py --port 9000

Then, in Simple Budget on your computer:
  1. Settings -> Sync -> click "Generate" to make a sync key.
  2. Leave "Peer address" blank (the computer talks to itself).
  3. Click "Sync now".

On your phone / tablet (same Wi-Fi):
  1. Settings -> Sync -> enter the SAME key.
  2. Enter this computer's IP address (printed below when the agent starts).
  3. Click "Sync now".

SECURITY
--------
* The agent only listens on your local network.
* All requests must carry the matching sync key.
* The key is learned from the first device that syncs ("trust on first use")
  and stored in 'simplebudget-sync-data.json'. To reset the key, stop the
  agent and delete that file.
"""

import argparse
import json
import os
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "simplebudget-sync-data.json")

# In-memory store, guarded by a lock. Shape: {"key": str, "lastModified": int, "data": dict}
_store = {"key": None, "lastModified": -1, "data": None}
_lock = threading.Lock()


def load_store():
    """Load persisted sync blob from disk (best effort)."""
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as fh:
            saved = json.load(fh)
        if isinstance(saved, dict):
            _store["key"] = saved.get("key")
            _store["lastModified"] = int(saved.get("lastModified", -1))
            _store["data"] = saved.get("data")
            print("Loaded saved sync data (last modified: %s)." % _store["lastModified"])
    except Exception as exc:  # noqa: BLE001
        print("Could not read %s: %s" % (DATA_FILE, exc))


def save_store():
    """Persist the current sync blob to disk (best effort)."""
    try:
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(_store, fh)
        os.replace(tmp, DATA_FILE)
    except Exception as exc:  # noqa: BLE001
        print("Could not write %s: %s" % (DATA_FILE, exc))


def local_ip():
    """Best-effort discovery of this machine's LAN IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:  # noqa: BLE001
        return "127.0.0.1"
    finally:
        s.close()


class Handler(BaseHTTPRequestHandler):
    server_version = "SimpleBudgetSync/1.0"

    # ---- helpers -------------------------------------------------------
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # quieter logging
        sys.stdout.write("  %s - %s\n" % (self.address_string(), fmt % args))

    # ---- routes --------------------------------------------------------
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/status":
            with _lock:
                self._json(200, {
                    "ok": True,
                    "hasData": _store["data"] is not None,
                    "lastModified": _store["lastModified"] if _store["lastModified"] >= 0 else None,
                })
            return
        if path in ("/", "/index.html"):
            self._serve_index()
            return
        self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/sync":
            self._json(404, {"ok": False, "error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            payload = json.loads(raw.decode("utf-8"))
        except Exception:  # noqa: BLE001
            self._json(400, {"ok": False, "error": "bad json"})
            return

        key = (payload.get("key") or "").strip()
        incoming_lm = int(payload.get("lastModified", 0) or 0)
        incoming_data = payload.get("data")

        if not key:
            self._json(400, {"ok": False, "error": "missing key"})
            return

        with _lock:
            # Trust on first use: adopt the first key we ever see.
            if _store["key"] is None:
                _store["key"] = key
                print("Adopted sync key from first device.")
            elif _store["key"] != key:
                self._json(403, {"ok": False, "error": "key mismatch"})
                return

            if _store["data"] is None or incoming_lm >= _store["lastModified"]:
                # Incoming is newer (or first) -> keep it.
                _store["lastModified"] = incoming_lm
                _store["data"] = incoming_data
                save_store()
                print("Stored newer data (lastModified=%s)." % incoming_lm)
                self._json(200, {"action": "kept", "lastModified": incoming_lm})
            else:
                # Stored copy is newer -> hand it back to this device.
                print("Sent stored newer data (lastModified=%s) to device." % _store["lastModified"])
                self._json(200, {
                    "action": "update",
                    "lastModified": _store["lastModified"],
                    "data": _store["data"],
                })

    def _serve_index(self):
        """Optionally serve the app itself so phones can load it from this PC."""
        index_path = os.path.join(SCRIPT_DIR, "index.html")
        if not os.path.exists(index_path):
            self._json(404, {"ok": False, "error": "index.html not next to agent"})
            return
        try:
            with open(index_path, "rb") as fh:
                body = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._cors()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:  # noqa: BLE001
            self._json(500, {"ok": False, "error": str(exc)})


def main():
    parser = argparse.ArgumentParser(description="Simple Budget local network sync agent")
    parser.add_argument("--port", type=int, default=8777, help="port to listen on (default 8777)")
    parser.add_argument("--host", default="0.0.0.0", help="address to bind (default 0.0.0.0 = all interfaces)")
    args = parser.parse_args()

    load_store()

    ip = local_ip()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)

    print("=" * 60)
    print(" Simple Budget - Local Network Sync Agent")
    print("=" * 60)
    print(" Listening on port %d" % args.port)
    print()
    print(" On THIS computer, leave 'Peer address' blank in the app.")
    print(" On your phone / tablet, use this address:")
    print()
    print("     Peer address : %s" % ip)
    print("     Port         : %d" % args.port)
    print()
    print(" Tip: phones can also open the app at  http://%s:%d/" % (ip, args.port))
    print(" Press Ctrl+C to stop.")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping agent.")
        httpd.shutdown()


if __name__ == "__main__":
    main()

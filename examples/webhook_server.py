"""Receive and verify Airwallex webhooks.

Runs a dependency-free stdlib server; equivalent FastAPI and Flask handlers
are shown at the bottom. Register the endpoint and get its secret with:

    endpoint = client.webhook_endpoints.create(
        url="https://your-host/webhooks/airwallex",
        events=["transfer.settled"],
        version="2024-01-31",
    )
    print(endpoint.secret)  # shown once — store it safely

Then:  WEBHOOK_SECRET=whsec_... python examples/webhook_server.py
"""

from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from airwallex import WebhookSignatureError, webhooks

SECRET = os.environ.get("WEBHOOK_SECRET", "whsec_replace_me")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        raw_body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        try:
            event = webhooks.construct_event(
                payload=raw_body,  # MUST be the raw bytes, never re-serialised JSON
                timestamp=self.headers.get("x-timestamp", ""),
                signature=self.headers.get("x-signature", ""),
                secret=SECRET,
            )
        except WebhookSignatureError as err:
            print("rejected webhook:", err)
            self.send_response(400)
            self.end_headers()
            return

        print(f"verified event {event.id}: {event.name}")
        if event.name == "transfer.settled":
            transfer = event.data or {}
            print("  transfer settled:", transfer.get("id"))
        # Respond 200 quickly; do heavy work on a queue.
        self.send_response(200)
        self.end_headers()


def main() -> None:
    server = HTTPServer(("127.0.0.1", 8000), Handler)
    print("listening on http://127.0.0.1:8000 — POST webhooks here")
    server.serve_forever()


if __name__ == "__main__":
    main()


# --- FastAPI equivalent -----------------------------------------------------
# @app.post("/webhooks/airwallex")
# async def airwallex_webhook(request: Request):
#     try:
#         event = webhooks.construct_event(
#             payload=await request.body(),
#             timestamp=request.headers.get("x-timestamp", ""),
#             signature=request.headers.get("x-signature", ""),
#             secret=SECRET,
#         )
#     except WebhookSignatureError:
#         raise HTTPException(status_code=400, detail="invalid signature")
#     ...
#     return {"ok": True}

# --- Flask equivalent -------------------------------------------------------
# @app.post("/webhooks/airwallex")
# def airwallex_webhook():
#     try:
#         event = webhooks.construct_event(
#             payload=request.get_data(),           # raw bytes
#             timestamp=request.headers.get("x-timestamp", ""),
#             signature=request.headers.get("x-signature", ""),
#             secret=SECRET,
#         )
#     except WebhookSignatureError:
#         abort(400)
#     ...
#     return "", 200

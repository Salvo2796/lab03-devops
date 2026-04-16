import json
import os
import time
import uuid
from datetime import datetime, timezone

import requests
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource
from flask import Flask, g, jsonify, request

SERVICE_NAME = os.getenv("SERVICE_NAME", "frontend")
BACKEND_URL = os.getenv("BACKEND_URL", "")
APPINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")

resource = Resource.create({"service.name": SERVICE_NAME})

if APPINSIGHTS_CONNECTION_STRING:
    configure_azure_monitor(
        connection_string=APPINSIGHTS_CONNECTION_STRING,
        resource=resource,
    )

app = Flask(__name__)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_log(status_code: int, message: str = "request_completed") -> None:
    latency_ms = round((time.perf_counter() - g.start_time) * 1000, 2)

    record = {
        "timestamp": utc_now_iso(),
        "service": SERVICE_NAME,
        "level": "INFO" if status_code < 400 else "ERROR",
        "message": message,
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "status": int(status_code),
        "latency_ms": latency_ms,
        "client_ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "user_agent": request.headers.get("User-Agent"),
    }

    print(json.dumps(record), flush=True)


@app.before_request
def before_request() -> None:
    g.start_time = time.perf_counter()
    g.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))


@app.after_request
def after_request(response):
    write_log(response.status_code)
    response.headers["X-Request-Id"] = g.request_id
    return response


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": SERVICE_NAME}), 200


@app.get("/demo")
def demo():
    if not BACKEND_URL:
        return jsonify({"error": "backend_url_not_configured", "status": 500}), 500

    headers = {"X-Request-Id": g.request_id}
    response = requests.get(f"{BACKEND_URL}/work", headers=headers, timeout=5)

    return (
        jsonify(
            {
                "service": SERVICE_NAME,
                "message": "frontend completed",
                "backend_response": response.json(),
            }
        ),
        response.status_code,
    )


@app.get("/demo-error")
def demo_error():
    if not BACKEND_URL:
        return jsonify({"error": "backend_url_not_configured", "status": 500}), 500

    headers = {"X-Request-Id": g.request_id}
    response = requests.get(f"{BACKEND_URL}/work-error", headers=headers, timeout=5)

    return (
        jsonify(
            {
                "service": SERVICE_NAME,
                "message": "frontend completed with backend error path",
                "backend_response": response.json(),
            }
        ),
        response.status_code,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource

# =========================
# CONFIG
# =========================
SERVICE_NAME = os.getenv("SERVICE_NAME", "backend")
APPINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")

app = Flask(__name__)

# =========================
# OBSERVABILITY SETUP
# =========================
resource = Resource.create({"service.name": SERVICE_NAME})

print("APPINSIGHTS ENABLED:", bool(APPINSIGHTS_CONNECTION_STRING), flush=True)

if APPINSIGHTS_CONNECTION_STRING:
    configure_azure_monitor(
        connection_string=APPINSIGHTS_CONNECTION_STRING,
        resource=resource,
    )

try:
    FlaskInstrumentor().instrument_app(app)
except Exception as e:
    print("Flask instrumentation error:", e, flush=True)

# =========================
# UTILS
# =========================
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

# =========================
# REQUEST LIFECYCLE
# =========================
@app.before_request
def before_request() -> None:
    g.start_time = time.perf_counter()
    g.request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))


@app.after_request
def after_request(response):
    write_log(response.status_code)
    response.headers["X-Request-Id"] = g.request_id
    return response

# =========================
# ROUTES
# =========================
@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": SERVICE_NAME}), 200


@app.get("/work")
def work():
    delay = random.uniform(0.1, 0.8)
    time.sleep(delay)

    return jsonify(
        {
            "service": SERVICE_NAME,
            "message": "backend completed",
            "processing_time": round(delay, 3),
        }
    ), 200


@app.get("/work-error")
def work_error():
    return jsonify(
        {
            "service": SERVICE_NAME,
            "error": "simulated_backend_error",
            "status": 500,
        }
    ), 500


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
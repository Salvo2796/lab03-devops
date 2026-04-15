import os
import requests
from flask import Flask, jsonify

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")

app = Flask(__name__)

@app.get("/demo")
def demo():
    response = requests.get(f"{BACKEND_URL}/work", timeout=5)
    backend_data = response.json()

    return jsonify(
        {
            "service": "frontend",
            "message": "frontend completed",
            "backend_response": backend_data,
        }
    )

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "frontend"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
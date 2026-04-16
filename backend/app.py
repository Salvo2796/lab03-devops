import time
import random
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/work")
def work():
    delay = random.uniform(0.1, 0.8)
    time.sleep(delay)

    return jsonify(
        {
            "service": "backend",
            "message": "backend completed",
            "processing_time": round(delay, 3),
        }
    )

@app.get("/health")
def health():
    return jsonify({"status": "Modifica avvenuta", "service": "backend"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
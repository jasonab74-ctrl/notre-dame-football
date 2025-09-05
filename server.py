# server.py — minimal boot test (drop-in full file)
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.get("/")
def ok():
    return "Notre Dame Football — OK", 200

@app.get("/health")
def health():
    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)

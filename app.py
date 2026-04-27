from flask import Flask, request, jsonify, send_from_directory
import urllib.request
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")

db_url = os.getenv("DATABASE_URL")
print(f"Connecting to: {db_url}")

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/breakdown", methods=["POST"])
def breakdown():
    task = request.json.get("task", "")

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a productivity expert who breaks down big tasks into clear, actionable steps. Always respond ONLY with a valid JSON object — no markdown, no explanation, no extra text."
            },
            {
                "role": "user",
                "content": f'Break down this task into 5 to 8 specific, practical steps: "{task}"\n\nRespond ONLY with this JSON format:\n{{\n  "steps": [\n    {{ "title": "Short step title", "description": "One to two sentences on what to do and why." }}\n  ]\n}}'
            }
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
        method="POST"
    )

    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))

    content = data["choices"][0]["message"]["content"]
    return jsonify({"content": content})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

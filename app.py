import os
from flask import Flask, request, jsonify, send_from_directory
import urllib.request
import json
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")


def call_openai(messages):
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": messages
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

    return data["choices"][0]["message"]["content"]


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/breakdown", methods=["POST"])
def breakdown():
    task = request.json.get("task", "")

    content = call_openai([
        {
            "role": "system",
            "content": "You are a productivity expert who breaks down big tasks into clear, actionable steps. Always respond ONLY with a valid JSON object — no markdown, no explanation, no extra text."
        },
        {
            "role": "user",
            "content": (
                f'Break down this task into 5 to 8 specific, practical steps: "{task}"\n\n'
                'Respond ONLY with this JSON format:\n'
                '{\n'
                '  "steps": [\n'
                '    { "title": "Short step title", "description": "One to two sentences on what to do and why." }\n'
                '  ]\n'
                '}'
            )
        }
    ])

    return jsonify({"content": content})


@app.route("/schedule", methods=["POST"])
def schedule():
    task = request.json.get("task", "")
    steps = request.json.get("steps", [])
    total_days = request.json.get("total_days", 7)

    steps_text = "\n".join(
        [f'{i+1}. {s["title"]}: {s["description"]}' for i, s in enumerate(steps)]
    )

    content = call_openai([
        {
            "role": "system",
            "content": "You are a productivity and scheduling expert. Always respond ONLY with a valid JSON object — no markdown, no explanation, no extra text."
        },
        {
            "role": "user",
            "content": (
                f'Given this task: "{task}"\n\n'
                f'And these steps:\n{steps_text}\n\n'
                f'Create a realistic schedule that fits within {total_days} days. '
                'Assign each step a day number (starting from Day 1), a suggested time of day (Morning, Afternoon, or Evening), '
                'and an estimated duration in hours (can be a decimal like 1.5).\n\n'
                'Respond ONLY with this JSON format:\n'
                '{\n'
                '  "schedule": [\n'
                '    {\n'
                '      "step": 1,\n'
                '      "title": "Step title",\n'
                '      "day": 1,\n'
                '      "time_of_day": "Morning",\n'
                '      "duration_hours": 2,\n'
                '      "note": "Short tip or reason for this timing."\n'
                '    }\n'
                '  ]\n'
                '}'
            )
        }
    ])

    return jsonify({"content": content})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

import os
import re

import requests
from flask import Flask, request, render_template, jsonify, Response

LOG_FILE_PATH = "./app/logs/app.log"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
APP_URL = os.getenv("APP_URL")

app = Flask(__name__, static_folder="app/static", template_folder="app/templates")


@app.before_first_request
def before_first_request():
    open(LOG_FILE_PATH, 'w').close()


@app.route('/')
def index():
    return render_template("index.html", APP_URL=APP_URL)


@app.route('/logs', methods=["GET"])
def flask_logs():
    return Response(flask_logger(), mimetype="text/plain", content_type="text/event-stream")


@app.route('/logs', methods=["POST"])
async def logs():
    log_messages = request.data.decode("utf-8")
    send_logs(log_messages)
    return jsonify({"status": "Logged"})


def send_logs(log_messages: str):
    for line in log_messages.split('\n'):
        try:
            send_discord_message(re.split(">[a-zA-Z0-9]* ", line.strip())[1])
        except IndexError:
            pass


def send_discord_message(message: str):
    payload = {"content": message}
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    requests.post(f"https://discord.com/api/v8/channels/{CHANNEL_ID}/messages", data=payload, headers=headers)


def flask_logger():
    with open(LOG_FILE_PATH) as logs:
        data = logs.read()
        yield data.encode()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5_000))
    app.run(debug=True, host="0.0.0.0", port=port, threading=True)

import os
import time
import threading
import subprocess
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
COOKIES_FILE = os.path.join(BASE_DIR, "cookies.txt")

os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED = {".mp3", ".m4a", ".wav", ".aac", ".mp4", ".ogg", ".flac"}

sync_lock = threading.Lock()
sync_enabled = False
last_sync = {"ts": 0, "action": "idle", "sourceId": ""}


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/files")
def list_files():
    files = []

    for name in os.listdir(UPLOAD_DIR):
        path = os.path.join(UPLOAD_DIR, name)
        if os.path.isfile(path) and os.path.splitext(name)[1].lower() in ALLOWED:
            files.append({
                "name": name,
                "url": f"/static/uploads/{name}",
                "modified": os.path.getmtime(path)
            })

    files.sort(key=lambda item: item["modified"], reverse=True)
    return jsonify(files)


@app.post("/api/upload")
def upload_file():
    file = request.files.get("file")

    if not file or not file.filename:
        return jsonify(ok=False, error="Aucun fichier reçu"), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED:
        return jsonify(ok=False, error="Format audio non autorisé"), 400

    name = secure_filename(os.path.basename(file.filename))
    if not name:
        name = f"audio_{int(time.time())}{ext}"

    stem, suffix = os.path.splitext(name)
    destination = os.path.join(UPLOAD_DIR, name)
    number = 2

    while os.path.exists(destination):
        name = f"{stem}_{number}{suffix}"
        destination = os.path.join(UPLOAD_DIR, name)
        number += 1

    file.save(destination)
    return jsonify(ok=True, file=name, url=f"/static/uploads/{name}")


@app.post("/api/delete")
def delete_file():
    data = request.get_json(silent=True) or {}
    name = secure_filename(os.path.basename(data.get("file", "")))

    if not name:
        return jsonify(ok=False, error="Nom de fichier manquant"), 400

    path = os.path.abspath(os.path.join(UPLOAD_DIR, name))
    root = os.path.abspath(UPLOAD_DIR)

    if os.path.commonpath([path, root]) != root:
        return jsonify(ok=False, error="Chemin invalide"), 400

    try:
        if os.path.isfile(path):
            os.remove(path)
        return jsonify(ok=True)
    except OSError as exc:
        return jsonify(ok=False, error=str(exc)), 500


@app.get("/api/cookies/status")
def cookie_status():
    exists = os.path.isfile(COOKIES_FILE)
    return jsonify(
        exists=exists,
        size=os.path.getsize(COOKIES_FILE) if exists else 0
    )


@app.post("/api/cookies/upload")
def cookie_upload():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify(ok=False, error="Aucun fichier reçu"), 400

    content = file.read(2_000_000).decode("utf-8", errors="ignore")
    with open(COOKIES_FILE, "w", encoding="utf-8") as output:
        output.write(content)

    return jsonify(ok=True, size=len(content))


@app.post("/api/cookies/delete")
def cookie_delete():
    try:
        if os.path.isfile(COOKIES_FILE):
            os.remove(COOKIES_FILE)
        return jsonify(ok=True)
    except OSError as exc:
        return jsonify(ok=False, error=str(exc)), 500


@app.post("/api/youtube")
def youtube_download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url.startswith(("https://", "http://")):
        return jsonify(ok=False, error="URL invalide"), 400

    output = os.path.join(UPLOAD_DIR, "%(title).150s.%(ext)s")
    command = [
        "yt-dlp", "--no-playlist", "-x",
        "--audio-format", "mp3", "--audio-quality", "0",
        "-o", output
    ]

    if os.path.isfile(COOKIES_FILE):
        command.extend(["--cookies", COOKIES_FILE])

    command.append(url)

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=180
        )

        if result.returncode != 0:
            return jsonify(
                ok=False,
                error=(result.stderr or "Téléchargement échoué")[-1200:]
            ), 400

        return jsonify(ok=True, title="Téléchargement terminé")

    except FileNotFoundError:
        return jsonify(
            ok=False, error="yt-dlp n'est pas installé sur le serveur."
        ), 501
    except subprocess.TimeoutExpired:
        return jsonify(ok=False, error="Délai de téléchargement dépassé"), 504
    except Exception as exc:
        app.logger.exception("Erreur YouTube")
        return jsonify(ok=False, error=str(exc)), 500


@app.route("/api/sync", methods=["GET", "POST"])
def sync():
    global sync_enabled, last_sync

    if request.method == "GET":
        with sync_lock:
            return jsonify({
                "enabled": sync_enabled,
                "command": dict(last_sync)
            })

    data = request.get_json(silent=True) or {}
    action = data.get("action", "")

    with sync_lock:
        if action == "toggleSync":
            sync_enabled = bool(data.get("enabled", False))
            last_sync = {
                "action": "syncState",
                "enabled": sync_enabled,
                "sourceId": str(data.get("sourceId", "")),
                "ts": int(time.time() * 1000)
            }
            return jsonify(ok=True, enabled=sync_enabled, command=last_sync)

        if not sync_enabled:
            return jsonify(ok=True, ignored=True, enabled=False)

        last_sync = dict(data)
        last_sync["ts"] = int(time.time() * 1000)

        return jsonify(ok=True, enabled=True, command=last_sync)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000"))
    )

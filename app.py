import os, time, subprocess, re
from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE, "static", "uploads")
STATIC_FOLDER = os.path.join(BASE, "static")
COOKIES_FILE = os.path.join(BASE, "cookies.txt")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

ALLOWED = {".mp3",".m4a",".wav",".aac",".mp4",".ogg",".flac",".jpg",".jpeg",".png",".webp"}
last_sync = {"ts": 0, "action": "idle"}

def clean_filename(name):
    name = os.path.basename(name)
    # Ne nettoie que les caractères interdits par les systèmes de fichiers (/ \ : * ? " < > |)
    # Conserve TOUS les emojis, les espaces, les accents et le cyrillique
    name = re.sub(r'[/\\:\*\?"<>\|]', '_', name)
    return name.strip()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/files")
def api_files():
    files = []
    if os.path.exists(UPLOAD_FOLDER):
        for f in os.listdir(UPLOAD_FOLDER):
            fp = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(fp):
                ext = os.path.splitext(f)[1].lower()
                if ext in ALLOWED:
                    files.append({"name": f, "url": f"/static/uploads/{f}"})
    files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x["name"])), reverse=True)
    return jsonify(files)

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files:
        return jsonify({"ok": False}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"ok": False}), 400
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED:
        return jsonify({"ok": False, "error": "Format non autorisé"}), 400
    filename = clean_filename(file.filename) or f"audio_{int(time.time())}.m4a"
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({"ok": True, "file": filename})

@app.route("/api/delete", methods=["POST"])
def api_delete():
    data = request.get_json() or {}
    name = data.get("file", "")
    if not name:
        return jsonify({"ok": False}), 400
    for p in [os.path.join(UPLOAD_FOLDER, clean_filename(name)), os.path.join(UPLOAD_FOLDER, name)]:
        if os.path.exists(p) and os.path.commonpath([p, UPLOAD_FOLDER]) == UPLOAD_FOLDER:
            try: os.remove(p)
            except: pass
    return jsonify({"ok": True})

@app.route("/api/cookies/status")
def cookies_status():
    if os.path.exists(COOKIES_FILE):
        return jsonify({"exists": True, "size": os.path.getsize(COOKIES_FILE)})
    return jsonify({"exists": False, "size": 0})

@app.route("/api/cookies/upload", methods=["POST"])
def cookies_upload():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "Aucun fichier"}), 400
    file = request.files["file"]
    data = file.read().decode('utf-8', errors='ignore')
    with open(COOKIES_FILE, "w", encoding="utf-8") as out:
        out.write(data)
    return jsonify({"ok": True, "size": len(data)})

@app.route("/api/youtube", methods=["POST"])
def api_youtube():
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return jsonify({"ok": False, "error": "URL invalide"}), 400
    out = os.path.join(UPLOAD_FOLDER, "%(title)s.%(ext)s")
    cmd = ["yt-dlp", "--no-playlist", "-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", out, url]
    if os.path.exists(COOKIES_FILE):
        cmd[1:1] = ["--cookies", COOKIES_FILE]
    else:
        cmd[1:1] = ["--user-agent", "Mozilla/5.0"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            err = r.stderr[-800:]
            return jsonify({"ok": False, "error": err}), 400
        return jsonify({"ok": True, "title": "Téléchargé avec succès"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/sync", methods=["GET", "POST"])
def api_sync():
    global last_sync
    if request.method == "POST":
        try:
            d = request.get_json()
            if d:
                last_sync = d
                last_sync["ts"] = time.time() * 1000
        except: pass
        return jsonify({"ok": True})
    return jsonify(last_sync)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(STATIC_FOLDER, filename)

@app.route("/static/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

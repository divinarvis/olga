# server.py V10.1 - fix bgutil once error - CLEAN
from flask import Flask, request, jsonify, send_from_directory
import pathlib
import re
import os
import yt_dlp

app = Flask(__name__)
BASE = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

def clean_yt_url(u):
    m = re.search(r'(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})', u or '')
    if m:
        return f"https://www.youtube.com/watch?v={m.group(1)}"
    return u

@app.route("/")
def index():
    return send_from_directory(str(BASE), "index.html")

@app.route("/assets/<path:p>")
def assets(p):
    return send_from_directory(str(BASE / "assets"), p)

@app.route("/uploads/<path:p>")
def uploads(p):
    return send_from_directory(str(UPLOAD_DIR), p)

@app.route("/api/sync", methods=["GET", "POST"])
@app.route("/api/portal/sync", methods=["GET", "POST"])
def sync():
    return jsonify({"action": "init"})

@app.route("/api/files")
def files():
    result = []
    for f in UPLOAD_DIR.glob("*"):
        if f.is_file():
            result.append({"name": f.name, "url": f"/uploads/{f.name}"})
    return jsonify(result)

@app.route("/api/delete", methods=["POST"])
def delete():
    try:
        data = request.get_json() or {}
        name = data.get("name")
        if name:
            (UPLOAD_DIR / name).unlink(missing_ok=True)
    except Exception:
        pass
    return jsonify({"ok": True})

@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"ok": False}), 400
    fn = re.sub(r'[^A-Za-z0-9_.-]', '_', f.filename or "a.m4a")
    f.save(UPLOAD_DIR / fn)
    return jsonify({"ok": True})

@app.route("/api/youtube", methods=["POST"])
def youtube():
    url = clean_yt_url((request.get_json() or {}).get("url") or "")
    if not url:
        return jsonify({"ok": False, "error": "no url"}), 400
    cookie = None
    for n in ["cookies.txt", "www.youtube.com_cookies.txt"]:
        p = BASE / n
        if p.exists():
            cookie = str(p)
            break
    opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': str(UPLOAD_DIR / '%(title)s.%(ext)s'),
        'noplaylist': True,
        'nocheckcertificate': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    if cookie:
        opts['cookiefile'] = cookie
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return jsonify({"ok": True, "title": info.get('title')})
    except Exception as e:
        print(e)
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

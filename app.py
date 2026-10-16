from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re, pathlib, traceback, urllib.parse, os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

BASE = pathlib.Path(".")
DOWNLOAD_DIR = BASE / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)
SYNC_DATA = {"ts": 0}

def clean_url(u):
    u = urllib.parse.unquote(u).strip()
    m = re.search(r'([A-Za-z0-9_-]{11})', u)
    if m:
        return f"https://www.youtube.com/watch?v={m.group(1)}"
    return u

@app.route("/")
def index():
    if (BASE / "index.html").exists():
        return send_from_directory(".", "index.html")
    return "SFBP LIVE"

@app.route("/<path:path>")
def static_files(path):
    if path.startswith("api/") or path.startswith("files/"):
        return "Not found", 404
    p = BASE / path
    if p.exists() and p.is_file():
        return send_from_directory(".", path)
    if (BASE / "index.html").exists():
        return send_from_directory(".", "index.html")
    return "SFBP LIVE"

@app.route("/api/files")
def list_files():
    files = []
    for p in DOWNLOAD_DIR.iterdir():
        if p.is_file():
            files.append({"name": p.name, "url": f"/files/{urllib.parse.quote(p.name)}"})
    return jsonify(files)

@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename)

# --- UPLOAD MP3 ---
@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files.get('file')
    if not f: return jsonify({"ok": False}), 400
    name = f.filename.split("\\")[-1].split("/")[-1]
    f.save(DOWNLOAD_DIR / name)
    return jsonify({"ok": True})

# --- UPLOAD COOKIES.TXT DEPUIS PHONE ---
@app.route("/api/cookies/upload", methods=["POST"])
def upload_cookies():
    try:
        # Via fichier
        if 'file' in request.files:
            f = request.files['file']
            content = f.read().decode('utf-8', errors='ignore')
        else:
            # Via texte collé
            data = request.get_json(force=True) or {}
            content = data.get('content','')

        if "# Netscape HTTP Cookie File" not in content and "youtube.com" not in content.lower():
            # on accepte quand même mais on prévient
            print("Cookies file seems invalid", flush=True)

        with open(BASE / "cookies.txt", "w", encoding="utf-8") as out:
            out.write(content)

        return jsonify({"ok": True, "msg": f"cookies.txt saved {len(content)} bytes"})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/cookies/status")
def cookies_status():
    p = BASE / "cookies.txt"
    if p.exists():
        return jsonify({"ok": True, "exists": True, "size": p.stat().st_size})
    return jsonify({"ok": True, "exists": False})

@app.route("/api/delete", methods=["POST"])
def delete():
    data = request.get_json(force=True) or {}
    fname = data.get("file","").split("\\")[-1].split("/")[-1]
    p = DOWNLOAD_DIR / fname
    if p.exists(): p.unlink()
    return jsonify({"ok": True})

@app.route("/api/sync", methods=["GET","POST"])
@app.route("/api/portal/sync", methods=["GET","POST"])
def sync():
    global SYNC_DATA
    if request.method == "POST":
        SYNC_DATA = request.get_json(force=True) or {}
        return jsonify({"ok": True})
    return jsonify(SYNC_DATA)

@app.route("/api/yt", methods=["GET"])
def yt():
    try:
        raw = request.query_string.decode(errors='ignore')
        url = raw.split("url=",1)[1] if "url=" in raw else request.args.get('url','')
        url = urllib.parse.unquote(url)
        url = clean_url(url)
        print(f"FINAL URL: {url}", flush=True)
        import yt_dlp
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            'js_runtimes': {'deno': {}},
            'remote_components': ['ejs:github'],
            'extractor_args': {'youtube': {'player_client': ['ios','android','mweb','web','tv_embedded'], 'player_skip': ['webpage','configs']}},
        }
        if os.path.exists("cookies.txt"):
            opts['cookiefile'] = 'cookies.txt'
            print("Using cookies.txt", flush=True)

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        return jsonify({"ok": True, "title": info.get('title')})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/youtube", methods=["POST","GET"])
def yt_compat():
    if request.method == "POST":
        try:
            data = request.get_json(force=True) or {}
            url = clean_url(data.get("url",""))
            import yt_dlp
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
                'noplaylist': True,
                'nocheckcertificate': True,
                'js_runtimes': {'deno': {}},
                'remote_components': ['ejs:github'],
                'extractor_args': {'youtube': {'player_client': ['ios','android','mweb','web','tv_embedded'], 'player_skip': ['webpage','configs']}},
            }
            if os.path.exists("cookies.txt"):
                opts['cookiefile'] = 'cookies.txt'
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            return jsonify({"ok": True, "title": info.get('title')})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500
    else:
        return yt()

@app.route("/api/youtube/stop", methods=["POST"])
@app.route("/api/stop", methods=["POST"])
def stop():
    return jsonify({"ok": True})

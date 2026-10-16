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
    return "SFBP LIVE - ajoute index.html"

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

@app.route("/api/upload", methods=["POST"])
def upload():
    try:
        f = request.files.get('file')
        if not f:
            return jsonify({"ok": False, "error": "no file"}), 400
        name = f.filename.split("\\")[-1].split("/")[-1]
        f.save(DOWNLOAD_DIR / name)
        return jsonify({"ok": True, "file": name})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/delete", methods=["POST"])
def delete():
    try:
        data = request.get_json(force=True) or {}
        fname = data.get("file","").split("\\")[-1].split("/")[-1]
        p = DOWNLOAD_DIR / fname
        if p.exists():
            p.unlink()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

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

        if not url:
            return jsonify({"ok": False, "error": "no url"}), 400

        import yt_dlp
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            'js_runtimes': {'deno': {}},
            'remote_components': ['ejs:github'],
            'extractor_args': {
                'youtube': {
                    'player_client': ['ios', 'android', 'mweb', 'web', 'tv_embedded'],
                    'player_skip': ['webpage', 'configs'],
                }
            },
        }
        # Si cookies.txt existe, on l'utilise
        if os.path.exists("cookies.txt"):
            opts['cookiefile'] = 'cookies.txt'
            print("Using cookies.txt", flush=True)
        else:
            print("NO cookies.txt - trying without", flush=True)

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

        return jsonify({"ok": True, "title": info.get('title')})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": f"{str(e)}"}), 500

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
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'android', 'mweb', 'web', 'tv_embedded'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
            }
            if os.path.exists("cookies.txt"):
                opts['cookiefile'] = 'cookies.txt'
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            return jsonify({"ok": True, "title": info.get('title')})
        except Exception as e:
            traceback.print_exc()
            return jsonify({"ok": False, "error": str(e)}), 500
    else:
        return yt()

@app.route("/api/youtube/stop", methods=["POST"])
@app.route("/api/stop", methods=["POST"])
def stop():
    return jsonify({"ok": True})

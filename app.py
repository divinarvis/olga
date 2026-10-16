from flask import Flask, request, jsonify
from flask_cors import CORS
import re, pathlib, traceback, urllib.parse, os

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = pathlib.Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def clean_url(u):
    u = urllib.parse.unquote(u).strip()
    # On cherche un ID de 10 ou 11 caractères
    m = re.search(r'([A-Za-z0-9_-]{10,11})', u)
    if m:
        return f"https://www.youtube.com/watch?v={m.group(1)}"
    return u

@app.route("/")
def home():
    return "SFBP LIVE"

@app.route("/api/yt")
def yt():
    try:
        # Récupère tout après url= même avec des & dedans
        raw = request.query_string.decode(errors='ignore')
        if "url=" in raw:
            url = raw.split("url=", 1)[1]
        else:
            url = request.args.get('url', '')

        url = urllib.parse.unquote(url)
        url = clean_url(url)
        print(f"FINAL CLEAN URL: {url}", flush=True)

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
            'extractor_args': {'youtube': {'player_client': ['ios', 'android_tv', 'web']}},
        }

        if os.path.exists("cookies.txt"):
            opts['cookiefile'] = 'cookies.txt'
            print("USING COOKIES", flush=True)

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

        return jsonify({"ok": True, "title": info.get('title'), "url": url})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": f"ERROR: {str(e)}"}), 500

from flask import Flask, request, jsonify
from flask_cors import CORS
import re, pathlib, traceback, urllib.parse

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = pathlib.Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def clean_url(u):
    u = urllib.parse.unquote(u)
    # On prend juste l'ID de 11 caractères, on jette tout le reste (&feature, etc)
    m = re.search(r'([A-Za-z0-9_-]{11})', u)
    if m:
        return f"https://www.youtube.com/watch?v={m.group(1)}"
    return u

@app.route("/")
def home():
    return "SFBP LIVE"

@app.route("/api/yt")
def yt():
    try:
        raw = request.query_string.decode()
        url = raw.split("url=",1)[1] if "url=" in raw else request.args.get('url','')
        url = urllib.parse.unquote(url)
        url = clean_url(url)
        print(f"FINAL CLEAN URL: {url}")

        import yt_dlp, os
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            'extractor_args': {'youtube': {'player_client': ['ios','android']}},
            'remote_components': ['ejs:github'],
        }
        if os.path.exists("cookies.txt"):
            opts['cookiefile'] = 'cookies.txt'

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

        return jsonify({"ok": True, "title": info.get('title')})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

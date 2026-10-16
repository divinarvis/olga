from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback, pathlib, re, glob

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "SFBP LIVE"

@app.route("/api/yt")
def yt():
    try:
        url = request.args.get('url','')
        print(f"YT REQUEST: {url}")
        if not url:
            return jsonify({"ok":False,"error":"no url"}), 400

        import yt_dlp
        DOWNLOAD_DIR = pathlib.Path("downloads")
        DOWNLOAD_DIR.mkdir(exist_ok=True)

        m = re.search(r'(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})', url)
        if m:
            url = f"https://www.youtube.com/watch?v={m.group(1)}"

        opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            'extractor_args': {'youtube': {'player_client': ['ios']}},
            'remote_components': ['ejs:github'],
        }

        import os
        if os.path.exists("cookies.txt"):
            opts['cookiefile'] = 'cookies.txt'
            print("USING COOKIES")

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

        return jsonify({"ok": True, "title": info.get('title')})

    except Exception as e:
        print("ERROR YT:", e)
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

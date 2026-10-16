from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp, re, pathlib, glob

app = Flask(__name__)
CORS(app)
DOWNLOAD_DIR = pathlib.Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def clean_url(u):
    m = re.search(r'(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})', u or '')
    return f"https://www.youtube.com/watch?v={m.group(1)}" if m else u

CLIENTS = [['ios'], ['web_safari','ios'], ['tv_embedded'], ['web','ios']]

def download_yt(url):
    url = clean_url(url)
    for client in CLIENTS:
        opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            'extractor_args': {'youtube': {'player_client': client}},
            'remote_components': ['ejs:github'],
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}],
        }
        if pathlib.Path("cookies.txt").exists():
            opts['cookiefile'] = 'cookies.txt'
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            mp3s = sorted(glob.glob(str(DOWNLOAD_DIR / "*.mp3")), key=lambda x: pathlib.Path(x).stat().st_mtime, reverse=True)
            if mp3s: return mp3s[0], info.get('title','audio')
    raise Exception("block")

@app.route("/api/yt")
def api_yt():
    url = request.args.get('url')
    mp3_path, title = download_yt(url)
    return jsonify({"ok": True, "file": pathlib.Path(mp3_path).name})

@app.route("/api/upload", methods=['POST'])
def upload():
    f = request.files.get('file')
    (DOWNLOAD_DIR / f.filename).write_bytes(f.read()) if hasattr(f,'read') else f.save(DOWNLOAD_DIR / f.filename)
    return jsonify({"ok": True})

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
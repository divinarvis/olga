# Copie ce fichier complet sur GitHub server.py
from flask import Flask, request, jsonify, send_from_directory
import pathlib, re, os, json
import yt_dlp
app = Flask(__name__)
BASE = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
SYNC_FILE = BASE / "sync.json"
if not SYNC_FILE.exists():
    SYNC_FILE.write_text('{"ts":0}', encoding='utf-8')
def clean_yt_url(u):
    import re
    m = re.search(r'(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})', u or '')
    if m: return f"https://www.youtube.com/watch?v={m.group(1)}"
    return u
@app.route("/")
def index(): return send_from_directory(str(BASE), "index.html")
@app.route("/assets/<path:p>")
def assets(p): return send_from_directory(str(BASE / "assets"), p)
@app.route("/uploads/<path:p>")
def uploads(p): return send_from_directory(str(UPLOAD_DIR), p)
@app.route("/api/sync", methods=["GET","POST"])
@app.route("/api/portal/sync", methods=["GET","POST"])
def sync():
    if request.method=="POST":
        data=request.get_json() or {}
        SYNC_FILE.write_text(json.dumps(data), encoding='utf-8')
        return jsonify({"ok":True})
    else:
        try: return jsonify(json.loads(SYNC_FILE.read_text(encoding='utf-8')))
        except: return jsonify({"ts":0})
@app.route("/api/files")
def files():
    result=[]
    for f in UPLOAD_DIR.glob("*"):
        if f.is_file(): result.append({"name": f.name, "url": f"/uploads/{f.name}"})
    return jsonify(result)
@app.route("/api/delete", methods=["POST"])
def delete_file():
    data=request.get_json() or {}
    name=data.get("file") or data.get("name")
    if name:
        p = UPLOAD_DIR / pathlib.Path(name).name
        if p.exists(): p.unlink()
    return jsonify({"ok":True})
@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f: return jsonify({"ok":False}),400
    safe = re.sub(r'[\\/]+','_', f.filename or "audio.mp3").strip()
    dest = UPLOAD_DIR / safe
    i=1
    base=safe
    while dest.exists():
        name, ext = os.path.splitext(base)
        dest = UPLOAD_DIR / f"{name}_{i}{ext}"
        i+=1
    f.save(dest)
    return jsonify({"ok":True, "file": dest.name})
@app.route("/api/youtube", methods=["POST"])
def youtube():
    url=clean_yt_url((request.get_json() or {}).get("url") or "")
    if not url: return jsonify({"ok":False, "error":"no url"}),400
    opts={'format':'bestaudio[ext=m4a]/bestaudio/best','outtmpl':str(UPLOAD_DIR / '%(title)s.%(ext)s'),'noplaylist':True,'nocheckcertificate':True,'postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}]}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info=ydl.extract_info(url, download=True)
            return jsonify({"ok":True, "title":info.get('title')})
    except Exception as e:
        return jsonify({"ok":False, "error":str(e)}),500
@app.route("/api/youtube/stop", methods=["POST"])
@app.route("/api/youtube/cancel", methods=["POST"])
@app.route("/api/stop", methods=["POST"])
@app.route("/api/kill", methods=["POST"])
def stop_dummy(): return jsonify({"ok":True})
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",8000)))

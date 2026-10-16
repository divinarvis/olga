# server.py V10.2 - DIVINARVIS V8.11.0 + FIX YT BOT 2026
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

@app.route("/api/sync", methods=["GET","POST"])
@app.route("/api/portal/sync", methods=["GET","POST"])
def sync():
    if request.method=="POST":
        try:
            data=request.get_json() or {}
            SYNC_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            return jsonify({"ok":True})
        except Exception as e:
            return jsonify({"ok":False, "error":str(e)}),500
    else:
        try:
            return jsonify(json.loads(SYNC_FILE.read_text(encoding='utf-8')))
        except:
            return jsonify({"ts":0})

@app.route("/api/files")
def files():
    result=[]
    for f in UPLOAD_DIR.glob("*"):
        if f.is_file():
            result.append({"name": f.name, "url": f"/uploads/{f.name}", "size": f.stat().st_size})
    result.sort(key=lambda x: x["name"])
    return jsonify(result)

@app.route("/api/delete", methods=["POST"])
def delete_file():
    try:
        data=request.get_json() or {}
        name=data.get("file") or data.get("name")
        if name:
            p = UPLOAD_DIR / pathlib.Path(name).name
            if p.exists():
                p.unlink()
        return jsonify({"ok":True})
    except Exception as e:
        return jsonify({"ok":False, "error":str(e)}),500

@app.route("/api/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify({"ok":False, "error":"no file"}),400
    raw_name = f.filename or "audio.mp3"
    safe = re.sub(r'[\\/]+','_', raw_name).strip()
    if not safe:
        safe="audio.mp3"
    dest = UPLOAD_DIR / safe
    i=1
    base=safe
    while dest.exists():
        name, ext = os.path.splitext(base)
        dest = UPLOAD_DIR / f"{name}_{i}{ext}"
        i+=1
        if i>100:
            break
    f.save(dest)
    return jsonify({"ok":True, "file": dest.name, "name": dest.name, "filename": dest.name})

@app.route("/api/youtube", methods=["POST"])
def youtube():
    data=request.get_json() or {}
    url=clean_yt_url(data.get("url") or "")
    if not url:
        return jsonify({"ok":False, "error":"no url"}),400

    cookie=None
    for n in ["cookies.txt","www.youtube.com_cookies.txt","youtube.com_cookies.txt"]:
        p=BASE / n
        if p.exists():
            cookie=str(p)
            break

    opts={
        'format':'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl':str(UPLOAD_DIR / '%(title)s.%(ext)s'),
        'noplaylist':True,
        'nocheckcertificate':True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'postprocessors':[{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}],
        'no_warnings': False,
        'ignoreerrors': False,
    }
    if cookie:
        opts['cookiefile']=cookie

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info=ydl.extract_info(url, download=True)
            title = info.get('title') or "youtube"
            return jsonify({"ok":True, "title": title})
    except Exception as e:
        print(f"YT ERROR: {e}")
        return jsonify({"ok":False, "error": str(e)}),500

@app.route("/api/youtube/stop", methods=["POST"])
@app.route("/api/youtube/cancel", methods=["POST"])
@app.route("/api/stop", methods=["POST"])
@app.route("/api/kill", methods=["POST"])
def stop_dummy():
    return jsonify({"ok":True})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",8000)))

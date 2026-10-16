# V16 - FIX "The page needs to be reloaded" - euuvveMhWsc VEVO
from flask import Flask, request, jsonify, send_from_directory
import pathlib, re, os, json, yt_dlp

app = Flask(__name__)
BASE = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
SYNC_FILE = BASE / "sync.json"
COOKIE_FILE = BASE / "cookies.txt"
if not SYNC_FILE.exists():
    SYNC_FILE.write_text('{"ts":0}', encoding='utf-8')

def clean_yt_url(u):
    if not u: return ""
    m=re.search(r'(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})', u)
    return f"https://www.youtube.com/watch?v={m.group(1)}" if m else u

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
        SYNC_FILE.write_text(json.dumps(request.get_json() or {}, ensure_ascii=False), encoding='utf-8')
        return jsonify({"ok":True})
    try: return jsonify(json.loads(SYNC_FILE.read_text(encoding='utf-8')))
    except: return jsonify({"ts":0})
@app.route("/api/files")
def files(): return jsonify([{"name":f.name,"url":f"/uploads/{f.name}"} for f in UPLOAD_DIR.glob("*") if f.is_file()])
@app.route("/api/delete", methods=["POST"])
def delete_file():
    n=(request.get_json() or {}).get("file") or (request.get_json() or {}).get("name")
    if n:
        p=UPLOAD_DIR / pathlib.Path(n).name
        if p.exists(): p.unlink()
    return jsonify({"ok":True})
@app.route("/api/upload", methods=["POST"])
def upload():
    f=request.files.get("file")
    if not f: return jsonify({"ok":False}),400
    safe=re.sub(r'[\\/]+','_', f.filename or "audio.mp3")
    dest=UPLOAD_DIR / safe
    i=1; b=safe
    while dest.exists():
        name,ext=os.path.splitext(b)
        dest=UPLOAD_DIR / f"{name}_{i}{ext}"; i+=1
    f.save(dest)
    return jsonify({"ok":True,"file":dest.name})
@app.route("/api/cookies", methods=["POST","GET","DELETE"])
def cookies_api():
    if request.method=="GET":
        return jsonify({"has_cookies": COOKIE_FILE.exists(), "size": COOKIE_FILE.stat().st_size if COOKIE_FILE.exists() else 0})
    if request.method=="DELETE":
        if COOKIE_FILE.exists(): COOKIE_FILE.unlink()
        return jsonify({"ok":True})
    f=request.files.get("file") or request.files.get("cookies")
    if not f: return jsonify({"ok":False}),400
    f.save(COOKIE_FILE)
    return jsonify({"ok":True})

@app.route('/api/youtube', methods=['POST'])
def youtube():
    data = request.get_json() or {}
    url = clean_yt_url(data.get("url", ""))
    if not url:
        return jsonify({"ok": False, "error": "URL manquante"}), 400

    cookie = None
    for n in ["cookies.txt", "www.youtube.com_cookies.txt"]:
        p = BASE / n
        if p.exists():
            cookie = str(p)
            break

    # On teste plusieurs clients, un va débloquer euuvve
    clients_to_try = [
        ['web_embedded'],
        ['web'],
        ['ios'],
        ['web', 'web_embedded'],
        ['web_safari', 'web'],
    ]

    last_err = ""
    for client in clients_to_try:
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(UPLOAD_DIR / '%(title)s.%(ext)s'),
            'noplaylist': True,
            'nocheckcertificate': True,
            'extractor_args': {'youtube': {'player_client': client}},
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
        }
        if cookie:
            opts['cookiefile'] = cookie

        try:
            print(f"TRYING CLIENT {client} for {url}")
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'audio') if info else 'audio'
                print(f"SUCCESS WITH CLIENT {client}")
                return jsonify({"ok": True, "title": title, "client": str(client)})
        except Exception as e:
            last_err = str(e)
            print(f"FAIL CLIENT {client}: {e}")
            if "needs to be reloaded" in last_err or "Sign in" in last_err:
                continue
            if "Requested format" in last_err:
                continue

    return jsonify({"ok": False, "error": last_err[:800]}), 500

@app.route("/api/version")
def version(): return jsonify({"v":"V16 multi-client fix reload"})
@app.route("/api/youtube/stop", methods=["POST"])
@app.route("/api/youtube/cancel", methods=["POST"])
@app.route("/api/stop", methods=["POST"])
@app.route("/api/kill", methods=["POST"])
def stop_dummy(): return jsonify({"ok":True})

if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",8000)))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re, pathlib, traceback, urllib.parse, os, sys

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

BASE = pathlib.Path(".")
DOWNLOAD_DIR = BASE / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)
SYNC_DATA = {"ts": 0}

def clean_url(u):
    u = urllib.parse.unquote(u).strip()
    # extrait l'ID 11 chars même si y'a?list= etc
    m = re.search(r'([A-Za-z0-9_-]{11})', u)
    if m:
        return f"https://www.youtube.com/watch?v={m.group(1)}"
    return u

@app.route("/")
def index():
    if (BASE / "index.html").exists():
        return send_from_directory(".", "index.html")
    return "SFBP LIVE V8.13"

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
        if p.is_file() and p.name!= "cookies.txt":
            files.append({"name": p.name, "url": f"/files/{urllib.parse.quote(p.name)}"})
    return jsonify(files)

@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename)

# --- UPLOAD MP3 ---
@app.route("/api/upload", methods=["POST"])
def upload():
    try:
        f = request.files.get('file')
        if not f: return jsonify({"ok": False, "error": "no file"}), 400
        name = f.filename.split("\\")[-1].split("/")[-1]
        # decode vrai nom russe si encodé
        try:
            name = urllib.parse.unquote(name)
        except:
            pass
        if not name:
            name = "upload.mp3"
        dest = DOWNLOAD_DIR / name
        f.save(dest)
        print(f"UPLOAD OK: {name} {dest.stat().st_size} bytes", flush=True)
        return jsonify({"ok": True, "file": name})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

# --- UPLOAD COOKIES.TXT DEPUIS PHONE - V8.13 ---
@app.route("/api/cookies/upload", methods=["POST"])
def upload_cookies():
    try:
        content = ""
        # Via fichier
        if 'file' in request.files:
            f = request.files['file']
            content = f.read().decode('utf-8', errors='ignore')
        else:
            # Via JSON
            data = request.get_json(force=True, silent=True) or {}
            content = data.get('content','')

        if not content.strip():
            # Effacer
            for p in [BASE / "cookies.txt", DOWNLOAD_DIR / "cookies.txt"]:
                if p.exists():
                    p.unlink()
            print("COOKIES CLEARED", flush=True)
            return jsonify({"ok": True, "msg": "cookies effacés"})

        # Validation basique
        if "youtube.com" not in content and "google.com" not in content and "# Netscape" not in content:
            print(f"COOKIES INVALID: {content[:200]}", flush=True)
            return jsonify({"ok": False, "error": "Fichier invalide, doit contenir youtube.com"}), 400

        # Sauve aux deux endroits pour être sûr
        for p in [BASE / "cookies.txt", DOWNLOAD_DIR / "cookies.txt"]:
            with open(p, "w", encoding="utf-8") as out:
                out.write(content)

        print(f"COOKIES SAVED: {len(content)} bytes", flush=True)
        return jsonify({"ok": True, "msg": f"cookies.txt sauvé {len(content)} bytes", "size": len(content)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/cookies/status")
def cookies_status():
    p = BASE / "cookies.txt"
    p2 = DOWNLOAD_DIR / "cookies.txt"
    target = p if p.exists() else p2
    if target.exists():
        size = target.stat().st_size
        # lit un peu pour check validité
        try:
            txt = target.read_text(encoding="utf-8", errors="ignore")[:1000]
            has_yt = "youtube.com" in txt or "google.com" in txt
        except:
            has_yt = True
        return jsonify({"ok": True, "exists": True, "size": size, "valid": has_yt})
    return jsonify({"ok": True, "exists": False, "size": 0})

@app.route("/api/delete", methods=["POST"])
def delete():
    try:
        data = request.get_json(force=True) or {}
        fname = data.get("file","").split("\\")[-1].split("/")[-1]
        if not fname:
            return jsonify({"ok": False}), 400
        p = DOWNLOAD_DIR / fname
        p2 = BASE / fname
        deleted = False
        if p.exists():
            p.unlink()
            deleted = True
        if p2.exists() and fname == "cookies.txt":
            p2.unlink()
            deleted = True
        return jsonify({"ok": True, "deleted": deleted})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/sync", methods=["GET","POST"])
@app.route("/api/portal/sync", methods=["GET","POST"])
def sync():
    global SYNC_DATA
    if request.method == "POST":
        try:
            SYNC_DATA = request.get_json(force=True) or {}
        except:
            pass
        return jsonify({"ok": True})
    return jsonify(SYNC_DATA)

def get_yt_opts():
    """Opts intelligents: AVEC cookies on garde WEB, SANS cookies on bypass"""
    has_cookies = False
    cookie_path = None
    for cand in [BASE / "cookies.txt", DOWNLOAD_DIR / "cookies.txt"]:
        if cand.exists() and cand.stat().st_size > 1000:
            has_cookies = True
            cookie_path = str(cand)
            break

    opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
        'noplaylist': True,
        'nocheckcertificate': True,
        'js_runtimes': {'deno': {}},
        'remote_components': ['ejs:github'],
        'quiet': False,
        'no_warnings': False,
    }

    if has_cookies:
        opts['cookiefile'] = cookie_path
        # AVEC cookies on DOIT utiliser web, pas skip webpage
        opts['extractor_args'] = {'youtube': {'player_client': ['web', 'ios', 'mweb']}}
        print(f"YT OPTS: WITH COOKIES {cookie_path}", flush=True)
    else:
        # SANS cookies, on tente bypass
        opts['extractor_args'] = {'youtube': {'player_client': ['ios','android','mweb','web','tv_embedded'], 'player_skip': ['webpage','configs']}}
        print("YT OPTS: NO COOKIES - bypass mode", flush=True)

    return opts

@app.route("/api/yt", methods=["GET"])
def yt():
    try:
        raw = request.query_string.decode(errors='ignore')
        url = raw.split("url=",1)[1] if "url=" in raw else request.args.get('url','')
        url = urllib.parse.unquote(url)
        url = clean_url(url)
        print(f"FINAL YT URL: {url}", flush=True)
        import yt_dlp

        opts = get_yt_opts()
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        title = info.get('title','OK')
        print(f"YT SUCCESS: {title}", flush=True)
        return jsonify({"ok": True, "title": title})
    except Exception as e:
        traceback.print_exc()
        err = str(e)
        # Message clair pour ton screen
        if "Sign in to confirm you're not a bot" in err or "bot" in err.lower():
            err = err + " -> UPLOAD un vrai cookies.txt connecté 10k+ bytes avec httpOnly"
        return jsonify({"ok": False, "error": err}), 500

@app.route("/api/youtube", methods=["POST","GET"])
def yt_compat():
    if request.method == "POST":
        try:
            data = request.get_json(force=True) or {}
            url = clean_url(data.get("url",""))
            print(f"FINAL YT POST URL: {url}", flush=True)
            import yt_dlp
            opts = get_yt_opts()
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            return jsonify({"ok": True, "title": info.get('title','OK')})
        except Exception as e:
            traceback.print_exc()
            err = str(e)
            if "Sign in to confirm you're not a bot" in err:
                err = err + " -> Ton cookies.txt de 4782b est trop petit, refais export CONNECTÉ httpOnly"
            return jsonify({"ok": False, "error": err}), 500
    else:
        return yt()

@app.route("/api/youtube/stop", methods=["POST"])
@app.route("/api/stop", methods=["POST"])
def stop():
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

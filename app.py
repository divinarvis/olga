import os
import re
import time
import threading
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import quote

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
COOKIES_FILE = BASE_DIR / "cookies.txt"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED = {".mp3", ".m4a", ".wav", ".aac", ".mp4", ".ogg", ".flac", ".webm"}
MAX_UPLOAD_BYTES = 512 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

sync_lock = threading.Lock()
sync_enabled = False
last_sync = {"ts": 0, "action": "idle", "sourceId": ""}


def clean_filename(filename: str, fallback_ext: str = "") -> str:
    """Conserve les accents tout en retirant les caracteres dangereux."""
    raw = unicodedata.normalize("NFC", str(filename or "").strip())
    raw = raw.replace("\\", "/").split("/")[-1]
    raw = "".join(ch for ch in raw if ch >= " " and ch not in '<>:"/\\|?*')
    raw = re.sub(r"\s+", " ", raw).strip(" .")

    if not raw:
        raw = f"fichier_{int(time.time())}{fallback_ext}"

    stem, ext = os.path.splitext(raw)
    ext = ext.lower() or fallback_ext
    stem = stem.strip(" .") or f"fichier_{int(time.time())}"
    return f"{stem[:180]}{ext}"


def unique_destination(filename: str) -> tuple[str, Path]:
    name = clean_filename(filename)
    stem, suffix = os.path.splitext(name)
    destination = UPLOAD_DIR / name
    number = 2

    while destination.exists():
        name = f"{stem} ({number}){suffix}"
        destination = UPLOAD_DIR / name
        number += 1

    return name, destination


def safe_existing_path(filename: str) -> Path | None:
    """Resout strictement un nom deja stocke sans autoriser de sortie du dossier."""
    raw = unicodedata.normalize("NFC", str(filename or "").strip())
    if not raw or raw in {".", ".."} or Path(raw).name != raw:
        return None

    candidate = (UPLOAD_DIR / raw).resolve()
    root = UPLOAD_DIR.resolve()

    try:
        candidate.relative_to(root)
    except ValueError:
        return None

    return candidate


def public_file(name: str) -> dict:
    path = UPLOAD_DIR / name
    return {
        "name": name,
        "displayName": Path(name).stem,
        "url": f"/static/uploads/{quote(name, safe='')}",
        "modified": path.stat().st_mtime,
        "size": path.stat().st_size,
        "source": "youtube" if name.lower().endswith(".mp3") else "local",
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(
        ok=True,
        service="DIVINARVIS Media Player",
        siri=False,
        navigation="iphone",
        timestamp=int(time.time() * 1000),
    )


@app.get("/api/files")
def list_files():
    files = []

    try:
        for path in UPLOAD_DIR.iterdir():
            if path.is_file() and path.suffix.lower() in ALLOWED:
                files.append(public_file(path.name))
    except OSError as exc:
        return jsonify(ok=False, error=str(exc)), 500

    files.sort(key=lambda item: item["modified"], reverse=True)
    return jsonify(files)


@app.post("/api/upload")
def upload_file():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return jsonify(ok=False, error="Aucun fichier recu"), 400

    original_name = unicodedata.normalize("NFC", uploaded.filename)
    ext = Path(original_name).suffix.lower()

    if ext not in ALLOWED:
        return jsonify(ok=False, error="Format audio ou video non autorise"), 400

    name, destination = unique_destination(original_name)

    try:
        uploaded.save(destination)
        return jsonify(ok=True, file=public_file(name))
    except OSError as exc:
        return jsonify(ok=False, error=f"Enregistrement impossible : {exc}"), 500


@app.post("/api/delete")
def delete_file():
    data = request.get_json(silent=True) or {}
    path = safe_existing_path(data.get("file", ""))

    if path is None:
        return jsonify(ok=False, error="Nom de fichier invalide"), 400
    if not path.exists() or not path.is_file():
        return jsonify(ok=False, error="Fichier introuvable"), 404
    if path.suffix.lower() not in ALLOWED:
        return jsonify(ok=False, error="Type de fichier non autorise"), 400

    try:
        path.unlink()
        return jsonify(ok=True, deleted=path.name)
    except OSError as exc:
        return jsonify(ok=False, error=f"Suppression impossible : {exc}"), 500


@app.post("/api/delete-all")
def delete_all_files():
    deleted = []
    failed = []

    try:
        paths = list(UPLOAD_DIR.iterdir())
    except OSError as exc:
        return jsonify(ok=False, error=str(exc)), 500

    for path in paths:
        if path.is_file() and path.suffix.lower() in ALLOWED:
            try:
                path.unlink()
                deleted.append(path.name)
            except OSError as exc:
                failed.append({"file": path.name, "error": str(exc)})

    status = 207 if failed else 200
    return jsonify(ok=not failed, deleted=deleted, failed=failed), status


@app.get("/api/cookies/status")
def cookie_status():
    exists = COOKIES_FILE.is_file()
    return jsonify(
        exists=exists,
        size=COOKIES_FILE.stat().st_size if exists else 0,
    )


@app.post("/api/cookies/upload")
def cookie_upload():
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename:
        return jsonify(ok=False, error="Aucun fichier recu"), 400

    try:
        content = uploaded.read(2_000_000).decode("utf-8", errors="ignore")
        COOKIES_FILE.write_text(content, encoding="utf-8")
        return jsonify(ok=True, size=len(content))
    except OSError as exc:
        return jsonify(ok=False, error=f"Import des cookies impossible : {exc}"), 500


@app.post("/api/cookies/delete")
def cookie_delete():
    try:
        if COOKIES_FILE.is_file():
            COOKIES_FILE.unlink()
        return jsonify(ok=True)
    except OSError as exc:
        return jsonify(ok=False, error=str(exc)), 500


@app.post("/api/youtube")
def youtube_download():
    data = request.get_json(silent=True) or {}
    url = str(data.get("url") or "").strip()

    if not url.startswith(("https://", "http://")):
        return jsonify(ok=False, error="URL invalide"), 400

    try:
        before = {path.name for path in UPLOAD_DIR.iterdir() if path.is_file()}
    except OSError as exc:
        return jsonify(ok=False, error=str(exc)), 500

    output = str(UPLOAD_DIR / "%(title).150B.%(ext)s")
    command = [
        "yt-dlp",
        "--no-playlist",
        "--no-overwrites",
        "--windows-filenames",
        "--trim-filenames",
        "150",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--print",
        "after_move:filepath",
        "-o",
        output,
    ]

    if COOKIES_FILE.is_file():
        command.extend(["--cookies", str(COOKIES_FILE)])

    command.append(url)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=240,
        )

        if result.returncode != 0:
            return jsonify(
                ok=False,
                error=(result.stderr or "Telechargement echoue")[-1600:],
            ), 400

        after = {path.name for path in UPLOAD_DIR.iterdir() if path.is_file()}
        created = sorted(after - before)
        printed = [line.strip() for line in result.stdout.splitlines() if line.strip()]

        if not created and printed:
            candidate = Path(printed[-1]).name
            if (UPLOAD_DIR / candidate).is_file():
                created = [candidate]

        files = [
            public_file(name)
            for name in created
            if (UPLOAD_DIR / name).is_file()
        ]

        return jsonify(
            ok=True,
            title="Telechargement termine",
            files=files,
        )

    except FileNotFoundError:
        return jsonify(
            ok=False,
            error="yt-dlp n'est pas installe sur le serveur.",
        ), 501
    except subprocess.TimeoutExpired:
        return jsonify(ok=False, error="Delai de telechargement depasse"), 504
    except Exception as exc:
        app.logger.exception("Erreur YouTube")
        return jsonify(ok=False, error=str(exc)), 500


@app.route("/api/sync", methods=["GET", "POST"])
def sync():
    """Synchronisation entre les interfaces DIVINARVIS, sans Siri."""
    global sync_enabled, last_sync

    if request.method == "GET":
        with sync_lock:
            return jsonify(
                enabled=sync_enabled,
                command=dict(last_sync),
            )

    data = request.get_json(silent=True) or {}
    action = str(data.get("action") or "").strip()

    if not action:
        return jsonify(ok=False, error="Action de synchronisation manquante"), 400

    with sync_lock:
        if action == "toggleSync":
            sync_enabled = bool(data.get("enabled", False))
            last_sync = {
                "action": "syncState",
                "enabled": sync_enabled,
                "sourceId": str(data.get("sourceId") or "iphone"),
                "ts": int(time.time() * 1000),
            }
            return jsonify(
                ok=True,
                enabled=sync_enabled,
                command=dict(last_sync),
            )

        if not sync_enabled:
            return jsonify(ok=True, ignored=True, enabled=False)

        last_sync = dict(data)
        last_sync["sourceId"] = str(last_sync.get("sourceId") or "iphone")
        last_sync["ts"] = int(time.time() * 1000)

        return jsonify(
            ok=True,
            enabled=True,
            command=dict(last_sync),
        )


@app.errorhandler(413)
def too_large(_error):
    return jsonify(
        ok=False,
        error="Fichier trop volumineux (maximum 512 Mo)",
    ), 413


@app.errorhandler(404)
def not_found(_error):
    return jsonify(ok=False, error="Ressource introuvable"), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify(ok=False, error="Erreur interne du serveur"), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
    )

import os, time, subprocess, re
from flask import Flask, request, jsonify, send_from_directory, render_template_string

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE, "static", "uploads")
STATIC_FOLDER = os.path.join(BASE, "static")
COOKIES_FILE = os.path.join(BASE, "cookies.txt")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

ALLOWED = {".mp3",".m4a",".wav",".aac",".mp4",".ogg",".flac",".jpg",".jpeg",".png",".webp"}
last_sync = {"ts":0, "action":"idle"}

def clean_filename(name):
    name = os.path.basename(name)
    name = re.sub(r'[^\w\s\-\.\(\)\[\]àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇа-яА-ЯёЁ]', '_', name)
    return re.sub(r'\s+', ' ', name).strip()

HTML = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>DIVINARVIS V8.17 - Fixed Olga + Random</title>
<style>
:root{color-scheme:dark;--bg:#0d0408;--panel:rgba(22,9,16,.9);--panel2:rgba(33,12,23,.86);--line:rgba(244,63,94,.34);--text:#fff1f5;--muted:#c48b9f;--rose:#f43f5e;--violet:#d946ef;--cyan:#00f2ff;--green:#4ade80}
*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:linear-gradient(180deg,#15060d,#0d0408);color:var(--text);font-family:Inter,system-ui,-apple-system,sans-serif}
button,input{font:inherit}button{cursor:pointer}
.shell{width:min(1450px,96vw);margin:auto;padding:18px 0 30px}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 20px;border:1px solid var(--line);border-radius:22px;background:linear-gradient(180deg,rgba(38,12,26,.97),rgba(18,5,11,.95))}
.brand{display:flex;align-items:center;gap:14px}.logo{width:48px;height:48px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,var(--rose),var(--violet));font-weight:950;font-size:24px;color:#1a0208}
.brand h1{margin:0;font-size:24px;letter-spacing:.17em;font-weight:900}.brand small{display:block;color:var(--muted);font-size:11px;letter-spacing:.15em;margin-top:4px}
.onlineBox{display:flex;align-items:center;gap:10px;padding:10px 14px;border:1px solid var(--line);border-radius:14px;background:#18060f}.dot{width:10px;height:10px;border-radius:99px;background:#64748b}.dot.ok{background:var(--green);box-shadow:0 0 12px var(--green)}
.grid{display:grid;grid-template-columns:300px 1fr;gap:18px;margin-top:18px}.card{border:1px solid var(--line);border-radius:22px;background:linear-gradient(180deg,var(--panel2),var(--panel));overflow:hidden}
.cardHeader{display:flex;justify-content:space-between;align-items:center;padding:15px 17px;border-bottom:1px solid rgba(244,63,94,.12)}.cardHeader h2{margin:0;font-size:13px;letter-spacing:.12em;color:#ffd1df;text-transform:uppercase}
.profile{padding:18px;text-align:center}.portraitWrap{width:220px;aspect-ratio:1;margin:2px auto 14px;border-radius:50%;padding:7px;background:linear-gradient(135deg,var(--rose),var(--violet),#f5d06f)}.portrait{width:100%;height:100%;border-radius:50%;object-fit:cover;display:block;border:4px solid #14040a}
.profile h3{margin:8px 0 3px;font-size:24px}.tag{color:var(--rose);letter-spacing:.16em;font-size:11px}
.player{padding:18px}.now{display:flex;gap:18px;align-items:center}.cover{width:120px;height:120px;border-radius:18px;object-fit:cover;border:1px solid var(--line);flex-shrink:0}.nowTitle{font-size:22px;font-weight:900;margin:0 0 6px;word-break:break-word}.nowMeta{color:var(--muted);font-size:13px}
.controls{display:flex;gap:10px;margin:16px 0;justify-content:center;flex-wrap:wrap}.iconBtn{width:48px;height:48px;border-radius:14px;border:1px solid var(--line);background:#1a060f;color:white;font-size:20px;display:grid;place-items:center}
.iconBtn.play{width:62px;height:62px;border-radius:50%;background:linear-gradient(135deg,var(--rose),var(--violet));font-size:24px}
.iconBtn.love{width:auto;padding:0 20px;background:linear-gradient(135deg,#ff2d78,#ff5a8a);font-weight:900;font-size:13px;border-color:#ff2d78}.iconBtn.love.active{background:#fff;color:#ff2d78}
.iconBtn.loop{border-color:#a21caf}.iconBtn.loop.active{background:linear-gradient(135deg,#a21caf,#e11d48)}
.iconBtn.random{width:auto;padding:0 14px;border-color:var(--cyan);font-size:12px;font-weight:900}.iconBtn.random.active{background:var(--cyan);color:#000;box-shadow:0 0 15px var(--cyan)}
.playlist{padding:10px;max-height:360px;overflow:auto}.uploadBox{padding:16px;display:grid;gap:12px}.file{width:100%;padding:12px;border-radius:12px;background:#14040a;color:#fbcfe8;border:1px solid var(--line);font-size:16px}
.ytBox{display:grid;grid-template-columns:1fr 64px 64px;gap:10px;align-items:center}.ytInput{width:100%;padding:14px 16px;border-radius:14px;background:#14040a;color:#fbcfe8;border:1px solid rgba(244,63,94,.3);font-size:15px;outline:none}.ytBtn{height:48px;border-radius:14px;border:1px solid #e11d48;background:linear-gradient(135deg,#e11d48,#a21caf);color:white;font-weight:900;font-size:14px;display:grid;place-items:center}.ytStop{height:48px;border-radius:14px;border:1px solid rgba(251,113,133,.4);background:#1a060f;color:#fecdd3;font-weight:800;font-size:12px;display:grid;place-items:center}
.btn{padding:12px 14px;border-radius:13px;border:1px solid var(--line);background:#2b0a18;color:white;font-weight:800}.btn.primary{background:linear-gradient(135deg,#e11d48,#a21caf)}.btn.danger{border-color:rgba(251,113,133,.6);color:#fecdd3;background:#3a0a18}.btn.stop{background:#1a060f;border-color:#64748b;color:#cbd5e1}
.track{padding:12px;margin:6px 0;background:rgba(255,255,255,.06);border-radius:12px;display:flex;justify-content:space-between;align-items:center;border:1px solid transparent;gap:10px}.track.active{border-color:#f43f5e;background:rgba(244,63,94,.18)}
.delBtn{background:#1a060f;border:1px solid rgba(244,63,94,.5);color:#ff8fb0;border-radius:8px;padding:6px 10px;font-size:13px}
.log{max-height:140px;overflow:auto;font-family:ui-monospace,monospace;font-size:11px;color:#f4a2b8;padding:12px;line-height:1.6}.good{color:#86efac}.err{color:#fda4af}.warn{color:#fcd34d}
.footer{padding:16px;text-align:center;color:#8a4f65;font-size:11px}
#soundGate{position:fixed;inset:0;z-index:9999;background:rgba(13,4,8,.92);backdrop-filter:blur(12px);display:grid;place-items:center;padding:20px}#soundGate.hide{display:none}
.gateCard{width:min(420px,92vw);padding:28px 22px;border:1px solid rgba(244,63,94,.4);border-radius:22px;background:linear-gradient(180deg,rgba(38,12,26,.98),rgba(18,5,11,.98));text-align:center}
.gateBtn{margin-top:16px;width:100%;padding:18px 14px;border-radius:16px;border:1px solid #ff2d78;background:linear-gradient(135deg,#ff2d78,#7c2dff);color:white;font-weight:900;font-size:16px}
@media(max-width:430px){.shell{width:100vw;padding:10px}.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div id="soundGate"><div class="gateCard"><div style="font-size:48px">🔊</div><h2>DIVINARVIS V8.17</h2><div style="color:var(--muted);font-size:13px">OLGA MUSE • RANDOM • UTF-8 FIX</div><button type="button" class="gateBtn" id="gateBtn">▶️ ACTIVER LE SON</button></div></div>
<main class="shell">
<header class="topbar"><div class="brand"><div class="logo">D</div><div><h1>DIVINARVIS</h1><small>V8.17 • OLGA PROFILE FIXED</small></div></div><div class="onlineBox"><i class="dot ok"></i><div><strong id="syncStatus">ONLINE</strong></div></div></header>
<div class="grid">
<div>
<article class="card profile">
  <div class="portraitWrap">
    <img class="portrait" src="/static/olga.jpg" onerror="this.src='/static/olga.png'" alt="OLGA">
  </div>
  <h3>OLGA</h3>
  <div class="tag">DIVINARVIS MUSE</div>
</article>
<article class="card" style="margin-top:18px"><div class="cardHeader"><h2>Sync</h2></div><div style="padding:16px"><div style="display:grid;gap:10px;font-size:13px"><div style="display:flex;justify-content:space-between"><span style="color:var(--muted)">Playlist</span><span id="trackCount">0 morceau</span></div><div style="display:flex;justify-content:space-between"><span style="color:var(--muted)">Son</span><span id="soundState" style="color:#f43f5e;font-weight:800">🔇 BLOQUÉ</span></div><div style="display:flex;justify-content:space-between"><span style="color:var(--muted)">Mode</span><span id="loopState" style="color:var(--muted);font-weight:800">LOOP OFF</span></div><div style="display:flex;justify-content:space-between"><span style="color:var(--muted)">Cookies</span><span id="cookiesStatus" style="font-weight:800">...</span></div></div></div></article>
<article class="card" style="margin-top:18px"><div class="cardHeader"><h2>Journal</h2></div><div class="log" id="log"></div></article>
</div>
<div>
<article class="card"><div class="cardHeader"><h2>Media Control</h2><small id="liveHint" style="color:var(--muted)">SON BLOQUÉ</small></div><div class="player">
<div class="now">
  <img id="cover" class="cover" src="/static/olga.jpg" onerror="this.src='/static/olga.png'">
  <div><div class="nowTitle" id="title">Son bloqué</div><div class="nowMeta" id="meta">Clique pour activer.</div></div>
</div>
<audio id="audio" playsinline preload="metadata" crossorigin="anonymous"></audio>
<div class="controls">
<button type="button" class="iconBtn" id="prevBtn">⏮</button>
<button type="button" class="iconBtn play" id="playBtn">▶️</button>
<button type="button" class="iconBtn" id="nextBtn">⏭</button>
<button type="button" class="iconBtn loop" id="loopBtn">🔁</button>
<button type="button" class="iconBtn random" id="randomBtn">🔀 ALEATOIRE: OFF</button>
<button type="button" class="iconBtn love" id="loveRadioBtn">♥️ LOVE</button>
</div>
<div style="width:100%;height:4px;background:rgba(255,255,255,.1);border-radius:10px;overflow:hidden;margin-top:10px"><div id="progress" style="height:100%;width:0%;background:linear-gradient(90deg,#f43f5e,#d946ef)"></div></div></div></article>

<article class="card" style="margin-top:18px;border-color:#a21caf"><div class="cardHeader"><h2>🇬🇧 CAPITAL UK</h2></div><div style="padding:12px;display:grid;gap:8px">
<div class="track" id="cap1"><span style="flex:1"><b>Capital London</b></span><div style="display:flex;gap:6px"><button type="button" class="btn primary" id="playCap1">▶️</button><button type="button" class="btn stop" id="stopCap1">⏹️ STOP</button></div></div>
<div class="track" id="cap2"><span style="flex:1"><b>Capital XTRA</b></span><div style="display:flex;gap:6px"><button type="button" class="btn primary" id="playCap2">▶️</button><button type="button" class="btn stop" id="stopCap2">⏹️ STOP</button></div></div>
</div></article>

<div id="loveCast" style="display:none;margin-top:18px" class="card"><div class="cardHeader"><h2>♥️ LOVE RADIO</h2><button type="button" class="btn danger" style="padding:6px 10px" onclick="hideLoveCast()">FERMER</button></div><iframe id="loveIframe" src="" style="width:100%;height:700px;border:0;background:white"></iframe></div>

<article class="card" style="margin-top:18px"><div class="cardHeader"><h2>DIVINARVIS Playlist</h2><span id="trackCount2">0 piste</span></div><div class="playlist" id="playlist"></div></article>

<article class="card" style="margin-top:18px"><div class="cardHeader"><h2>Charger</h2></div><div class="uploadBox">
<div class="ytBox"><input id="ytInput" class="ytInput" type="text" placeholder="Colle 1 lien YouTube..."><button type="button" id="ytBtn" class="ytBtn">YT+</button><button type="button" id="ytStopBtn" class="ytStop">STOP</button></div>
<div id="ytStatus" style="font-size:11px;color:var(--muted)">YT prêt</div>

<div style="margin-top:8px; border:2px dashed #ff4d9d; padding:12px; border-radius:14px; background:rgba(255,77,157,.08);">
  <div style="font-size:13px; font-weight:900; margin-bottom:8px;">🍪 COOKIES YouTube</div>
  <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
    <input type="file" id="cookiesFile" accept=".txt" class="file" style="flex:1; min-width:140px; padding:8px;" />
    <button type="button" id="cookiesBtn" class="btn primary" style="padding:10px 14px; white-space:nowrap;">Uploader cookies.txt</button>
  </div>
  <div id="cookiesStatus2" style="font-size:12px; margin-top:8px; color:#c48b9f;">Vérification cookies...</div>
  <button type="button" id="clearCookiesBtn" class="btn danger" style="margin-top:8px; width:100%; padding:8px; font-size:12px;">🗑️ Effacer cookies.txt</button>
</div>

<input id="fileInput" class="file" type="file" accept=".mp3,.m4a,.wav,.aac,.mp4,audio/*" multiple>
<button type="button" id="clearShared" class="btn danger" style="width:100%">🗑️ EFFACER TOUTE LA PLAYLIST</button>
<button type="button" id="killYT" class="btn danger" style="width:100%;margin-top:6px;background:#7f1d1d;display:none">🚫 TUER LE DOWNLOAD YT</button>
</div></article>
</div>
</div>
<div class="footer">DIVINARVIS V8.17 • OLGA FIXED + RANDOM</div>
</main>
<script>
const $=id=>document.getElementById(id);
const log=(m,c='')=>{const el=$('log');const d=document.createElement('div');d.className=c;d.textContent='['+new Date().toLocaleTimeString()+'] '+m;el.prepend(d);};
const audio=$('audio'), playBtn=$('playBtn'), loveBtn=$('loveRadioBtn'), prevBtn=$('prevBtn'), nextBtn=$('nextBtn'), loopBtn=$('loopBtn'), randomBtn=$('randomBtn'), loopState=$('loopState'), loveCast=$('loveCast'), loveIframe=$('loveIframe');
const titleEl=$('title'), metaEl=$('meta'), hint=$('liveHint'), progress=$('progress');
const playlistEl=$('playlist'), trackCount=$('trackCount'), trackCount2=$('trackCount2');
const ytInput=$('ytInput'), ytBtn=$('ytBtn'), ytStopBtn=$('ytStopBtn'), killYTBtn=$('killYT'), ytStatus=$('ytStatus'), fileInput=$('fileInput'), clearBtn=$('clearShared');
const soundGate=$('soundGate'), gateBtn=$('gateBtn'), soundState=$('soundState'), syncStatus=$('syncStatus');
const cookiesFile=$('cookiesFile'), cookiesBtn=$('cookiesBtn'), cookiesStatus=$('cookiesStatus'), cookiesStatus2=$('cookiesStatus2'), clearCookiesBtn=$('clearCookiesBtn');
let tracks=[], current=-1, isLove=false, lastTs=0, soundUnlocked=false, isCapital=false, isLoop=false, randomMode=false, lastFilesHash="", currentRadioId=null;
let ytAbort=null, ytDownloading=false;
let trueNameMemory = new Map();
let recentUploads = [];

try{ const saved = JSON.parse(localStorage.getItem('divinarvis_true_names')||'{}'); for(const k in saved){ trueNameMemory.set(k, saved[k]); } }catch{}
function saveMemory(){ try{ const obj={}; for(const [k,v] of trueNameMemory){ obj[k]=v; } localStorage.setItem('divinarvis_true_names', JSON.stringify(obj)); }catch{} }
const seenSignatures = new Map();
function makeSig(file){ return `${file.name}::${file.size}::${file.lastModified}`; }
function isDuplicate(file){ const sig=makeSig(file); const now=Date.now(); for(const [k,t] of seenSignatures){ if(now-t>15000) seenSignatures.delete(k); } if(seenSignatures.has(sig)) return true; seenSignatures.set(sig, now); return false; }
function safeDecode(str){ if(!str) return ""; if(str.indexOf('%')===-1) return str

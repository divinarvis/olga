import os, time, subprocess
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE, "static", "uploads")
STATIC_FOLDER = os.path.join(BASE, "static")
COOKIES_FILE = os.path.join(BASE, "cookies.txt")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

ALLOWED = {".mp3",".m4a",".wav",".aac",".mp4",".ogg",".flac",".jpg",".jpeg",".png",".webp"}
last_sync = {"ts":0, "action":"idle"}

HTML = r"""
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>DIVINARVIS V8.17</title>
<style>
:root{color-scheme:dark;--bg:#0d0408;--panel:rgba(22,9,16,.9);--panel2:rgba(33,12,23,.86);--line:rgba(244,63,94,.34);--text:#fff1f5;--muted:#c48b9f;--rose:#f43f5e;--violet:#d946ef;--cyan:#00f2ff;--green:#4ade80}
*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:linear-gradient(180deg,#15060d,#0d0408);color:var(--text);font-family:Inter,-apple-system,sans-serif}
button,input{font:inherit}button{cursor:pointer}
.shell{width:min(1450px,96vw);margin:auto;padding:18px 0 30px}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 20px;border:1px solid var(--line);border-radius:22px;background:linear-gradient(180deg,rgba(38,12,26,.97),rgba(18,5,11,.95))}
.brand{display:flex;align-items:center;gap:14px}.logo{width:48px;height:48px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,var(--rose),var(--violet));font-weight:950;font-size:24px}
.brand h1{margin:0;font-size:24px;letter-spacing:.17em;font-weight:900}.brand small{display:block;color:var(--muted);font-size:11px}
.onlineBox{display:flex;align-items:center;gap:10px;padding:10px 14px;border:1px solid var(--line);border-radius:14px;background:#18060f}.dot{width:10px;height:10px;border-radius:99px;background:#64748b}.dot.ok{background:var(--green);box-shadow:0 0 12px var(--green)}
.grid{display:grid;grid-template-columns:300px 1fr;gap:18px;margin-top:18px}
.card{border:1px solid var(--line);border-radius:22px;background:linear-gradient(180deg,var(--panel2),var(--panel));overflow:hidden}
.cardHeader{display:flex;justify-content:space-between;align-items:center;padding:15px 17px;border-bottom:1px solid rgba(244,63,94,.12)}.cardHeader h2{margin:0;font-size:13px;letter-spacing:.12em;color:#ffd1df}
.profile{padding:18px;text-align:center}.portraitWrap{width:220px;aspect-ratio:1;margin:2px auto 14px;border-radius:50%;padding:7px;background:linear-gradient(135deg,var(--rose),var(--violet),#f5d06f);box-shadow:0 0 40px rgba(244,63,94,.3)}.portrait{width:100%;height:100%;border-radius:50%;object-fit:cover;display:block;border:4px solid #14040a}
.player{padding:18px}.now{display:flex;gap:18px;align-items:center}.cover{width:120px;height:120px;border-radius:18px;object-fit:cover;border:1px solid var(--line)}.nowTitle{font-size:22px;font-weight:900;margin:0 0 6px}.nowMeta{color:var(--muted);font-size:13px}
.controls{display:flex;gap:10px;margin:16px 0;justify-content:center;flex-wrap:wrap}.iconBtn{width:48px;height:48px;border-radius:14px;border:1px solid var(--line);background:#1a060f;color:white;font-size:20px;display:grid;place-items:center}
.iconBtn.play{width:62px;height:62px;border-radius:50%;background:linear-gradient(135deg,var(--rose),var(--violet));font-size:24px}
.iconBtn.love{width:auto;padding:0 20px;background:linear-gradient(135deg,#ff2d78,#ff5a8a);font-weight:900;font-size:13px}.iconBtn.love.active{background:linear-gradient(135deg,#ff0040,#ff5a8a);box-shadow:0 0 20px #ff2d78}
.iconBtn.loop{border-color:#a21caf}.iconBtn.loop.active{background:linear-gradient(135deg,#a21caf,#e11d48);box-shadow:0 0 15px rgba(162,28,175,.6)}
.iconBtn.random{width:auto;padding:0 16px;border-color:var(--cyan);font-size:12px;font-weight:900}.iconBtn.random.active{background:var(--cyan);color:#000;box-shadow:0 0 20px var(--cyan)}
.playlist{padding:10px;max-height:360px;overflow:auto}.uploadBox{padding:16px;display:grid;gap:10px}.file{width:100%;padding:12px;border-radius:12px;background:#14040a;color:#fbcfe8;border:1px solid var(--line);font-size:16px}
.ytBox{display:grid;grid-template-columns:1fr auto;gap:10px}.btn{padding:12px 14px;border-radius:13px;border:1px solid var(--line);background:#2b0a18;color:white;font-weight:800}.btn.primary{background:linear-gradient(135deg,#e11d48,#a21caf)}.btn.danger{border-color:rgba(251,113,133,.4);color:#fecdd3}
.track{padding:12px;margin:6px 0;background:rgba(255,255,255,.06);border-radius:12px;display:flex;justify-content:space-between;align-items:center;border:1px solid transparent;gap:10px}.track.active{border-color:#f43f5e;background:rgba(244,63,94,.18)}
.delBtn{background:#1a060f;border:1px solid rgba(244,63,94,.5);color:#ff8fb0;border-radius:8px;padding:6px 10px;font-size:13px}
.log{max-height:140px;overflow:auto;font-family:monospace;font-size:11px;color:#f4a2b8;padding:12px}
.footer{padding:16px;text-align:center;color:#8a4f65;font-size:11px}
#soundGate{position:fixed;inset:0;z-index:9999;background:rgba(13,4,8,.92);backdrop-filter:blur(12px);display:grid;place-items:center;padding:20px}#soundGate.hide{display:none}
.gateCard{width:min(420px,92vw);padding:28px 22px;border:1px solid rgba(244,63,94,.4);border-radius:22px;background:linear-gradient(180deg,rgba(38,12,26,.98),rgba(18,5,11,.98));text-align:center}
.gateBtn{margin-top:16px;width:100%;padding:18px;border-radius:16px;border:1px solid #ff2d78;background:linear-gradient(135deg,#ff2d78,#7c2dff);color:white;font-weight:900;font-size:16px}
.cookiesBox{padding:16px;border:2px dashed rgba(244,63,94,.5);border-radius:16px;background:rgba(244,63,94,.08)}
@media(max-width:700px){.grid{grid-template-columns:1fr}.cover{width:72px;height:72px}.nowTitle{font-size:17px}}
</style>
</head>
<body>
<div id="soundGate"><div class="gateCard"><div style="font-size:48px">🔊</div><h2>DIVINARVIS V8.17</h2><div style="color:var(--muted);font-size:13px">OLGA SUPERHERO • LOVE DANS LE PLAYER • NO-RELOAD</div><button class="gateBtn" id="gateBtn">▶️ ACTIVER LE SON</button></div></div>
<main class="shell">
<header class="topbar"><div class="brand"><div class="logo">D</div><div><h1>DIVINARVIS</h1><small>PORTAL V8.17 • FINAL • NO-RELOAD</small></div></div><div class="onlineBox"><i class="dot ok"></i><div><strong id="syncStatus">ONLINE</strong><span style="display:block;color:var(--muted);font-size:11px" id="trackCount">0 morceau</span></div></div></header>
<div class="grid">
<div>
<article class="card profile"><div class="portraitWrap"><img class="portrait" src="/static/olga.jpg" onerror="this.src='/static/uploads/olga.jpg'; this.onerror=function(){this.src='https://i.pravatar.cc/300?img=5'}" alt="OLGA"></div><h3>OLGA</h3><div style="color:var(--rose);letter-spacing:.16em;font-size:11px">DIVINARVIS SUPERHERO</div><p style="margin:12px auto 0;max-width:320px;color:#ffe4ed;font-style:italic;font-size:13px">« Toujours dans mon système. »</p></article>
<article class="card" style="margin-top:18px"><div class="cardHeader"><h2>Sync</h2><span style="font-size:11px;color:var(--muted)" id="loopState">LOOP OFF • RANDOM OFF</span></div><div style="padding:16px;display:grid;gap:10px;font-size:13px"><div style="display:flex;justify-content:space-between"><span style="color:var(--muted)">Serveur</span><span style="color:var(--green);font-weight:800">ONLINE</span></div><div style="display:flex;justify-content:space-between"><span style="color:var(--muted)">Mode</span><span style="color:var(--cyan);font-weight:800">NO-RELOAD 10s</span></div></div></article>
<article class="card" style="margin-top:18px"><div class="cardHeader"><h2>Journal</h2><span style="font-size:11px;color:var(--muted)">LIVE</span></div><div class="log" id="log"></div></article>
</div>
<div>
<article class="card"><div class="cardHeader"><h2>Media Control</h2><small id="liveHint" style="color:var(--muted)">SON BLOQUÉ</small></div>
<div class="player"><div class="now"><img id="cover" class="cover" src="/static/olga.jpg" onerror="this.src='/static/uploads/olga.jpg'"><div><div class="nowTitle" id="title">Son bloqué</div><div class="nowMeta" id="meta">Clique pour activer</div></div></div>
<audio id="audio" playsinline preload="metadata"></audio>
<div class="controls">
<button class="iconBtn" id="prevBtn">⏮</button>
<button class="iconBtn play" id="playBtn">▶️</button>
<button class="iconBtn" id="nextBtn">⏭</button>
<button class="iconBtn loop" id="loopBtn">🔁</button>
<button class="iconBtn random" id="randomBtn">🔀 ALEATOIRE: OFF</button>
<button class="iconBtn love" id="loveRadioBtn">♥️ LOVE</button>
</div>
<div style="width:100%;height:4px;background:rgba(255,255,255,.1);border-radius:10px;overflow:hidden;margin-top:10px"><div id="progress" style="height:100%;width:0%;background:linear-gradient(90deg,#f43f5e,#d946ef)"></div></div>
</div></article>
<article class="card" style="margin-top:18px;border-color:var(--cyan)"><div class="cardHeader"><h2>🇬🇧 CAPITAL UK</h2><span style="font-size:11px;color:var(--cyan)">DIRECT</span></div><div style="padding:12px;display:grid;gap:8px">
<div class="track"><span><b>Capital London</b> <small>95.8 FM</small></span><button class="btn primary" style="padding:8px 14px" onclick="playCapital('https://media-ice.musicradio.com/CapitalMP3','Capital London')">▶️</button></div>
<div class="track"><span><b>Capital XTRA</b> <small>Hip Hop</small></span><button class="btn primary" style="padding:8px 14px" onclick="playCapital('https://media-ice.musicradio.com/CapitalXTRANationalMP3','Capital XTRA')">▶️</button></div>
</div></article>
<article class="card" style="margin-top:18px"><div class="cardHeader"><h2>DIVINARVIS Playlist</h2><span id="trackCount2">0 piste</span></div><div class="playlist" id="playlist"></div><button id="clearShared" class="btn danger" style="width:92%;margin:10px 4%">🗑️ EFFACER TOUTE LA PLAYLIST</button></article>
<article class="card" style="margin-top:18px"><div class="cardHeader"><h2>Charger</h2><span style="font-size:11px;color:var(--muted)">YT + LOCAL + FIX NOMS iPhone</span></div><div class="uploadBox"><div class="ytBox"><input id="ytInput" class="file" type="text" placeholder="Colle lien YouTube / TikTok"><button id="ytBtn" class="btn primary">YT+</button></div><div id="ytStatus" style="font-size:11px;color:var(--muted)">YT OK • Cookies: <span id="cookieStatus">checking...</span></div><input id="fileInput" class="file" type="file" accept=".mp3,.m4a,.wav,.aac,.mp4,.ogg,.flac" multiple></div></article>
<article class="card" style="margin-top:18px"><div class="cardHeader"><h2>🛠️ FIX BOT YouTube</h2><span style="font-size:11px;color:#f0abfc">Phone + Watch</span></div><div class="uploadBox"><div class="cookiesBox"><div style="font-size:12px;color:#ffd1df;margin-bottom:8px">Charger cookies depuis téléphone</div><input id="cookieFile" class="file" type="file" accept=".txt"><button id="cookieBtn" class="btn primary" style="width:100%">📤 Uploader cookies.txt</button><div id="cookieInfo" style="font-size:11px;color:var(--muted);margin-top:8px">pas de cookies.txt</div></div></div></article>
</div></div>
<div class="footer">DIVINARVIS V8.17 • OLGA SUPERHERO + LOVE PLAYER + RANDOM + LOOP + NO-RELOAD + WATCH FIX</div>
</main>
<script>
const $=id=>document.getElementById(id);
const log=(m)=>{const el=$('log');const d=document.createElement('div');d.textContent='['+new Date().toLocaleTimeString()+'] '+m;el.prepend(d);};
const audio=$('audio'), playBtn=$('playBtn'), prevBtn=$('prevBtn'), nextBtn=$('nextBtn'), loopBtn=$('loopBtn'), randomBtn=$('randomBtn'), loveBtn=$('loveRadioBtn'), loopState=$('loopState'), syncStatus=$('syncStatus');
const titleEl=$('title'), metaEl=$('meta'), hint=$('liveHint'), progress=$('progress'), playlistEl=$('playlist'), trackCount=$('trackCount'), trackCount2=$('trackCount2');
const ytInput=$('ytInput'), ytBtn=$('ytBtn'), ytStatus=$('ytStatus'), fileInput=$('fileInput'), clearBtn=$('clearShared');
const soundGate=$('soundGate'), gateBtn=$('gateBtn'), cookieFile=$('cookieFile'), cookieBtn=$('cookieBtn'), cookieInfo=$('cookieInfo'), cookieStatus=$('cookieStatus');
let tracks=[], current=-1, isLove=false, isCapital=false, isLoop=false, randomMode=false, soundUnlocked=false, lastTs=0, myLastPush=0;

function unlockSound(){if(soundUnlocked) return; soundUnlocked=true; try{audio.muted=true; let p=audio.play(); if(p) p.then(()=>{audio.pause();audio.muted=false}).catch(()=>{audio.muted=false});}catch{} soundGate.classList.add('hide'); hint.textContent='SON ACTIF'; log('🔊 SON ACTIF'); localStorage.setItem('divinarvis_sound','1');}
gateBtn.addEventListener('click', unlockSound); if(localStorage.getItem('divinarvis_sound')==='1') unlockSound();

function render(){
  playlistEl.innerHTML=''; if(!tracks.length){playlistEl.innerHTML='<div style="padding:22px;text-align:center;color:var(--muted)">Aucune piste</div>'; return;}
  tracks.forEach((t,i)=>{
    let showName=t.name; try{showName=decodeURIComponent(showName)}catch{} if(showName.length>45) showName=showName.substring(0,38)+'...';
    const div=document.createElement('div'); div.className='track'+(i===current?' active':'');
    div.innerHTML=`<span style="flex:1;cursor:pointer;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" onclick="playIdx(${i})">${i+1}. ${showName}</span><div style="display:flex;gap:6px"><b style="font-size:10px;cursor:pointer" onclick="playIdx(${i})">PLAY</b><button class="delBtn" onclick="deleteTrack(${i})">🗑️</button></div>`;
    playlistEl.appendChild(div);
  });
  trackCount.textContent=tracks.length+' morceau'; trackCount2.textContent=tracks.length+' piste';
}
function pushSync(action){
  try{
    const now=Date.now(); myLastPush=now;
    const payload={action,index:current,isPlaying:!audio.paused,isLove,isCapital,isLoop,randomMode,capitalUrl:audio.src,capitalName:titleEl.textContent,ts:now};
    localStorage.setItem('divinarvis_sync',JSON.stringify(payload));
    fetch('/api/sync',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).catch(()=>{});
  }catch{}
}
window.playIdx=(i)=>{if(!soundUnlocked) unlockSound(); if(i<0||i>=tracks.length) return; current=i; const tr=tracks[i]; isLove=false; isCapital=false; loveBtn.classList.remove('active'); audio.src=tr.url; audio.load(); audio.play().catch(()=>{}); playBtn.textContent='⏸️'; titleEl.textContent=tr.name; metaEl.textContent=`Playlist ${i+1}/${tracks.length}`; render(); pushSync('playIdx');}
window.playCapital=(url,name)=>{if(!soundUnlocked) unlockSound(); isLove=false; isCapital=true; loveBtn.classList.remove('active'); audio.src=url; audio.load(); audio.play().catch(()=>{}); titleEl.textContent=name; metaEl.textContent='UK RADIO'; hint.textContent='ON AIR - '+name; playBtn.textContent='⏸️'; pushSync('capital');}
window.deleteTrack=async(i)=>{const name=tracks[i]?.name; if(!confirm(`Supprimer "${name}"?`)) return; try{await fetch('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({file:name})});}catch{} tracks.splice(i,1); if(current===i){audio.pause(); audio.src=''; current=-1;} if(current>i) current--; render(); log('🗑️ Supprimé: '+name); pushSync('delete');};
audio.addEventListener('timeupdate',()=>{if(audio.duration) progress.style.width=(audio.currentTime/audio.duration*100)+'%';});
audio.addEventListener('ended',()=>{ if(isLoop){audio.currentTime=0; audio.play();} else {nextTrack();} });
function nextTrack(){ if(!tracks.length) return; if(randomMode){ let nxt=Math.floor(Math.random()*tracks.length); if(tracks.length>1) while(nxt===current) nxt=Math.floor(Math.random()*tracks.length); playIdx(nxt);} else { if(current < tracks.length-1) playIdx(current+1); } }
function prevTrack(){ if(randomMode){ nextTrack(); return; } if(current>0) playIdx(current-1); }
playBtn.onclick=()=>{if(!soundUnlocked) unlockSound(); if(!audio.src&&tracks.length) playIdx(0); else if(audio.paused){audio.play(); playBtn.textContent='⏸️'; pushSync('resume');} else {audio.pause(); playBtn.textContent='▶️'; pushSync('pause');}};
prevBtn.onclick=prevTrack; nextBtn.onclick=nextTrack;
loopBtn.onclick=()=>{ isLoop=!isLoop; audio.loop=isLoop; if(isLoop){loopBtn.classList.add('active'); log('🔁 BOUCLE ON');} else {loopBtn.classList.remove('active'); log('🔁 BOUCLE OFF');} updateLoopRandomLabel(); pushSync('loop');};
randomBtn.onclick=()=>{ randomMode=!randomMode; if(randomMode){randomBtn.classList.add('active'); randomBtn.textContent='🔀 ALEATOIRE: ON'; log('🔀 ALEATOIRE ON');} else {randomBtn.classList.remove('active'); randomBtn.textContent='🔀 ALEATOIRE: OFF'; log('🔀 ALEATOIRE OFF');} updateLoopRandomLabel(); pushSync('random');};
function updateLoopRandomLabel(){ loopState.textContent=`LOOP ${isLoop?'ON':'OFF'} • RANDOM ${randomMode?'ON':'OFF'}`; }

// LOVE RADIO COMME AVANT - DANS LE PLAYER
loveBtn.addEventListener('click',()=>{
  if(!soundUnlocked) unlockSound();
  if(!isLove){
    isLove=true; isCapital=false;
    audio.src='https://loveradio.hostingradio.ru:8000/loveradio_128';
    audio.load();
    audio.play().catch(()=>{});
    loveBtn.classList.add('active');
    titleEl.textContent='Love Radio 106.6';
    metaEl.textContent='ON AIR - LOVE RADIO';
    hint.textContent='♥️ LOVE ON AIR';
    playBtn.textContent='⏸️';
    log('♥️ LOVE RADIO ON - DANS PLAYER');
  } else {
    isLove=false;
    audio.pause(); audio.src='';
    loveBtn.classList.remove('active');
    hint.textContent='PAUSE';
    playBtn.textContent='▶️';
    log('♥️ LOVE OFF');
  }
  pushSync('love');
});

async function loadFiles(){try{const r=await fetch('/api/files'); const files=await r.json(); const localOnly=tracks.filter(t=>t.local); tracks=[...localOnly, ...files.map(f=>({name:f.name,url:f.url,local:false}))]; render();}catch{}}
async function addYT(){const url=(ytInput.value||'').trim(); if(!url) return; ytBtn.disabled=true; ytBtn.textContent='...'; ytStatus.textContent='Téléchargement...'; try{const r=await fetch('/api/youtube',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})}); const j=await r.json(); if(j.ok){ytStatus.textContent='✅ '+j.title; log('✅ YT OK '+j.title); ytInput.value=''; setTimeout(loadFiles,1500);} else {ytStatus.textContent='❌ '+j.error; log('❌ '+j.error);}}catch(e){ytStatus.textContent='❌ Réseau';} ytBtn.disabled=false; ytBtn.textContent='YT+';}
ytBtn.addEventListener('click',addYT);
fileInput.addEventListener('change', (e)=>{
  if(!soundUnlocked) unlockSound();
  const files=Array.from(e.target.files); if(!files.length) return;
  log(`📁 ${files.length} fichier(s) local`);
  files.forEach(f=>{
    let rawName=f.name || `audio_${Date.now()}.m4a`;
    let cleanName=rawName.trim();
    if(!cleanName.includes('.')){ const ext=(f.type.split('/')[1]||'m4a').split(';')[0]; cleanName=cleanName+'.'+ext; }
    let displayName=cleanName; try{displayName=decodeURIComponent(cleanName)}catch{}
    const url=URL.createObjectURL(f);
    tracks.push({name:displayName,url:url,local:true});
    const fd=new FormData(); fd.append('file',f,cleanName);
    fetch('/api/upload',{method:'POST',body:fd}).then(r=>r.json()).then(j=>{if(j.ok) log(`✅ PC a reçu: ${displayName}`)}).catch(()=>{});
  });
  render(); if(current===-1) playIdx(0); fileInput.value='';
});
clearBtn.addEventListener('click',async()=>{if(!confirm('Effacer toute la playlist?')) return; try{await fetch('/api/clear',{method:'POST'});}catch{} tracks=[]; render(); audio.pause(); audio.src=''; log('Playlist effacée'); pushSync('clear');});
async function checkCookies(){try{const r=await fetch('/api/cookies/status'); const j=await r.json(); if(j.exists){cookieInfo.textContent=`✅ cookies.txt actif (${j.size} bytes)`; cookieInfo.style.color='#4ade80'; cookieStatus.textContent=`${j.size} bytes ✅`; cookieStatus.style.color='#4ade80';} else {cookieInfo.textContent='❌ pas de cookies.txt • YouTube bloquera'; cookieStatus.textContent='manquant ❌';}}catch{}}
checkCookies();
cookieBtn.addEventListener('click',async()=>{ const f=cookieFile.files[0]; if(!f){alert('Choisis cookies.txt'); return;} const fd=new FormData(); fd.append('file',f); cookieBtn.textContent='Upload...'; try{const r=await fetch('/api/cookies/upload',{method:'POST',body:fd}); const j=await r.json(); if(j.ok){log('✅ Cookies uploadés '+j.size+' bytes'); checkCookies(); alert('✅ Cookies actifs!');} else {alert('❌ '+j.error);}}catch{alert('Erreur upload')} cookieBtn.textContent='📤 Uploader cookies.txt'; });

// NO-RELOAD SYNC
function handleSyncData(d){
  if(!d || !d.ts) return;
  if(d.ts <= lastTs) return;
  if(Math.abs(d.ts - myLastPush) < 2500 && d.action !== 'watch_next' && d.action !== 'watch_prev' && d.action !== 'watch_toggle' && d.action !== 'watch_random') return;
  lastTs=d.ts; syncStatus.textContent=d.action||'ONLINE';
  if(d.action==='watch_next') nextTrack();
  else if(d.action==='watch_prev') prevTrack();
  else if(d.action==='watch_toggle'){ if(audio.paused){audio.play().catch(()=>{}); playBtn.textContent='⏸️';} else {audio.pause(); playBtn.textContent='▶️';} }
  else if(d.action==='watch_random') randomBtn.click();
  else if(d.action==='playIdx' && typeof d.index==='number' && d.index!==current) playIdx(d.index);
}
window.addEventListener('storage',(e)=>{ if(e.key==='divinarvis_sync'){ try{ handleSyncData(JSON.parse(e.newValue)); }catch{} }});
setInterval(async()=>{ try{ let r=await fetch('/api/sync?nocache='+Date.now()); if(r.ok){ const d=await r.json(); if(d.action && d.action.startsWith('watch_')) handleSyncData(d); } }catch{} }, 10000);

loadFiles();
log('DIVINARVIS V8.17 READY - LOVE PLAYER + NO-RELOAD + WATCH FIX');
</script>
</body>
</html>
"""

@app.route("/")
def index(): return render_template_string(HTML)

@app.route("/api/files")
def api_files():
    files=[]
    for f in os.listdir(UPLOAD_FOLDER):
        fp=os.path.join(UPLOAD_FOLDER,f)
        if os.path.isfile(fp):
            ext=os.path.splitext(f)[1].lower()
            if ext in ALLOWED:
                files.append({"name":f,"url":f"/static/uploads/{f}"})
    files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER,x["name"])), reverse=True)
    return jsonify(files)

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "file" not in request.files: return jsonify({"ok":False}),400
    file=request.files["file"]
    if not file.filename: return jsonify({"ok":False}),400
    filename=secure_filename(file.filename) or f"audio_{int(time.time())}.m4a"
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({"ok":True,"name":filename})

@app.route("/api/delete", methods=["POST"])
def api_delete():
    data=request.get_json() or {}
    name=data.get("file","")
    for p in [os.path.join(UPLOAD_FOLDER,secure_filename(name)), os.path.join(UPLOAD_FOLDER,name)]:
        if os.path.exists(p):
            try: os.remove(p)
            except: pass
    return jsonify({"ok":True})

@app.route("/api/clear", methods=["POST"])
def api_clear():
    for f in os.listdir(UPLOAD_FOLDER):
        try: os.remove(os.path.join(UPLOAD_FOLDER,f))
        except: pass
    return jsonify({"ok":True})

@app.route("/api/cookies/status")
def cookies_status():
    if os.path.exists(COOKIES_FILE): return jsonify({"exists":True,"size":os.path.getsize(COOKIES_FILE)})
    return jsonify({"exists":False,"size":0})

@app.route("/api/cookies/upload", methods=["POST"])
def cookies_upload():
    if "file" not in request.files: return jsonify({"ok":False,"error":"no file"}),400
    data=request.files["file"].read().decode('utf-8', errors='ignore')
    if "# Netscape" not in data and "youtube.com" not in data.lower(): return jsonify({"ok":False,"error":"Fichier invalide"}),400
    if len(data)<500: return jsonify({"ok":False,"error":f"Trop petit {len(data)} bytes"}),400
    with open(COOKIES_FILE,"w",encoding="utf-8") as out: out.write(data)
    return jsonify({"ok":True,"size":len(data)})

@app.route("/api/youtube", methods=["POST"])
def api_youtube():
    data=request.get_json() or {}
    url=data.get("url","").strip()
    if not url: return jsonify({"ok":False,"error":"URL vide"}),400
    out=os.path.join(UPLOAD_FOLDER, "%(title)s.%(ext)s")
    cmd=["yt-dlp","--no-playlist","-x","--audio-format","mp3","--audio-quality","0","-o",out, url]
    if os.path.exists(COOKIES_FILE): cmd[1:1]=["--cookies", COOKIES_FILE]
    else: cmd[1:1]=["--user-agent","Mozilla/5.0"]
    try:
        r=subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode!=0:
            err=r.stderr[-800:]
            return jsonify({"ok":False,"error":err}),400
        return jsonify({"ok":True,"title":"OK"})
    except Exception as e:
        return jsonify({"ok":False,"error":str(e)}),500

@app.route("/api/sync", methods=["GET","POST"])
def api_sync():
    global last_sync
    if request.method=="POST":
        try:
            d=request.get_json()
            if d: last_sync=d; last_sync["ts"]=time.time()*1000
        except: pass
        return jsonify({"ok":True})
    return jsonify(last_sync)

@app.route("/api/watch/next")
def watch_next():
    global last_sync; last_sync={"action":"watch_next","ts":time.time()*1000}; return jsonify({"ok":True})
@app.route("/api/watch/prev")
def watch_prev():
    global last_sync; last_sync={"action":"watch_prev","ts":time.time()*1000}; return jsonify({"ok":True})
@app.route("/api/watch/toggle")
def watch_toggle():
    global last_sync; last_sync={"action":"watch_toggle","ts":time.time()*1000}; return jsonify({"ok":True})
@app.route("/api/watch/random")
def watch_random():
    global last_sync; last_sync={"action":"watch_random","ts":time.time()*1000}; return jsonify({"ok":True})
@app.route("/api/watch/play/<int:index>")
def watch_play(index):
    global last_sync; last_sync={"action":"playIdx","index":index,"ts":time.time()*1000}; return jsonify({"ok":True})

@app.route("/static/<path:filename>")
def serve_static(filename): return send_from_directory(STATIC_FOLDER, filename)
@app.route("/static/uploads/<path:filename>")
def serve_upload(filename): return send_from_directory(UPLOAD_FOLDER, filename)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))

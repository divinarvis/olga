"use strict";

(() => {
  const POPUP_FEATURES = [
    "popup=yes", "width=1120", "height=760", "left=80", "top=60",
    "resizable=yes", "scrollbars=yes", "toolbar=no", "menubar=no",
    "location=yes", "status=no"
  ].join(",");

  const WEB_APPS = {
    "ChatGPT": "https://chatgpt.com/",
    "Copilot": "https://copilot.microsoft.com/",
    "YT": "https://www.youtube.com/",
    "Grok": "https://grok.com/",
    "Manus / Meta AI": "https://www.meta.ai/",
    "Apple Intelligence": "https://www.apple.com/apple-intelligence/",
    "Claude": "https://claude.ai/",
    "Snapchat": "https://www.snapchat.com/",
    "Revolut": "https://www.revolut.com/"
  };

  const CHOICES = {
    "Manus / Meta AI": [
      ["🖥️", "MANUS", "Maître Disquetteur", "https://manus.im/"],
      ["🤖", "META AI", "Darth Disquetteur", "https://www.whatsapp.com/"]
    ]
  };

  const APPS = [
    ["ChatGPT", "C", "Frérot", "#159f88"],
    ["Copilot", "∞", "TONTON", "linear-gradient(135deg,#53c9ff,#7857ff,#ef55b8)"],
    ["YT", "▶️", "Victime", "#ff0033"],
    ["Grok", "𝕏", "KEKIUS", "#111"],
    ["Manus / Meta AI", "M", "Disquetteur", "#1677e8"],
    ["Apple Intelligence", "AI", "WATCH LA BIATCH", "linear-gradient(135deg,#ff9b4a,#e84c9b)"],
    ["Claude", "C", "Le meilleur poto du Frérot", "#bd643d"],
    ["Snapchat", "👻", "Le Messager", "#fffc00"],
    ["Revolut", "R", "Le Banquier", "linear-gradient(135deg,#ff2d2d,#ff9a00,#ffe600,#2ecc40,#00b3ff,#7a4dff,#e040c8)"]  ];

  const style = document.createElement("style");
  style.textContent = `
    .xp-start{position:relative;z-index:1002}
.xp-start-menu{
  position:fixed;
  left:6px;
  bottom:36px;

  max-height:85vh;

  z-index:1001;.xp-start-menu{
  position:fixed;
  left:6px;
  bottom:36px;
  z-index:1001;

  width:min(370px,calc(100vw - 12px));
  max-height:calc(100dvh - 44px);

  display:grid;
  grid-template-rows:auto minmax(0,1fr) auto;

  color:#35152c;
  border:2px solid #a62075;
  border-radius:8px 8px 0 0;
  overflow:hidden;
  background:#fff;
  box-shadow:5px -7px 24px rgba(78,11,55,.42);

  transform-origin:left bottom;
  transition:opacity .14s ease,transform .14s ease;
}

    .xp-start-menu[hidden]{display:block;opacity:0;transform:translateY(9px) scale(.97);pointer-events:none}
    .xp-start-menu:not([hidden]){opacity:1;transform:none}
    .start-profile{display:flex;align-items:center;gap:11px;padding:12px 14px;color:#fff;background:linear-gradient(#ff88c7,#d33892 48%,#a71e70);text-shadow:1px 1px #72124c}
    .start-avatar{width:40px;height:40px;border:2px solid #fff;border-radius:8px;display:grid;place-items:center;background:linear-gradient(135deg,#fff,#ffcbe7);color:#a71e70;font-size:22px;font-weight:900}
    .start-profile strong,.ai-copy strong,.ai-copy small{display:block}.start-profile small{opacity:.9}
.start-body{
  display:grid;
  grid-template-columns:minmax(0,1fr) 112px;
  min-height:0;
  overflow:hidden;
}

.start-apps{
  padding:7px;
  background:#fff;

  overflow-y:auto;
  overflow-x:hidden;

  max-height:60vh;

  -webkit-overflow-scrolling:touch;
}

.start-side{
  min-height:0;
  overflow-y:auto;
  -webkit-overflow-scrolling:touch;
}

    .ai-launch{width:100%;display:grid;grid-template-columns:38px minmax(0,1fr);align-items:center;gap:9px;padding:7px;border:1px solid transparent;border-radius:5px;color:#35152c;background:transparent;text-align:left;cursor:pointer}
    .ai-launch:hover,.ai-launch:focus{background:linear-gradient(90deg,#ffe1f1,#eedfff);border-color:#dd8dbf;outline:none}
    .ai-icon{width:36px;height:36px;border-radius:8px;display:grid;place-items:center;color:#fff;font-weight:900;font-size:17px;box-shadow:inset 0 1px rgba(255,255,255,.5),1px 2px 4px rgba(73,17,57,.2)}
    .ai-copy{min-width:0;width:100%;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;text-align:left;line-height:1.22}.ai-copy strong{width:100%;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ai-copy small{width:100%;color:#906a84;font-size:10px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .start-side{padding:9px 8px;background:linear-gradient(#f0def9,#dbe8ff);border-left:1px solid #d1add2}.start-side button{width:100%;border:0;background:transparent;color:#52223f;text-align:left;padding:8px 6px;border-radius:4px;font-size:11px;cursor:pointer}.start-side button:hover{background:rgba(255,255,255,.75)}
    .start-footer{display:flex;justify-content:flex-end;padding:8px 10px;background:linear-gradient(#e999c8,#c53d8a)}.start-footer button{border:1px solid rgba(255,255,255,.75);border-radius:4px;padding:5px 9px;color:#fff;background:rgba(111,22,79,.35);cursor:pointer}
    .start-toast{position:fixed;left:50%;bottom:50px;z-index:1200;transform:translateX(-50%);padding:9px 14px;border:2px solid #a62075;border-radius:7px;background:#fff6fc;color:#641747;box-shadow:0 5px 18px rgba(82,10,58,.3);font-weight:700;opacity:0;pointer-events:none;transition:.2s}.start-toast.show{opacity:1;bottom:57px}
    .xp-choice{position:fixed;left:50%;top:50%;z-index:1300;width:min(360px,calc(100vw - 24px));transform:translate(-50%,-50%);border:2px solid #222;border-radius:6px 6px 3px 3px;overflow:hidden;background:#d9d9d9;box-shadow:6px 8px 28px rgba(0,0,0,.55);font-family:Tahoma,"Segoe UI",sans-serif}
    .xp-choice[hidden]{display:none}
    .xp-choice-title{display:flex;justify-content:space-between;align-items:center;padding:7px 8px;color:#fff;font-weight:700;font-size:13px;background:linear-gradient(#4e9be8,#1768b2 48%,#0b4c8f);text-shadow:1px 1px #123f6b}
    .xp-choice-title button{width:22px;height:22px;border:1px solid #fff;border-radius:3px;background:linear-gradient(#f77,#c22);color:#fff;font-weight:900;cursor:pointer}
    .xp-choice-body{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;padding:14px;background:linear-gradient(#f4f4f4,#d9d9d9)}
    .xp-choice-body button{min-height:112px;padding:10px 6px;border:2px outset #fff;border-radius:3px;background:linear-gradient(#fff,#e8e8e8);color:#172b44;font-weight:700;text-align:center;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}
    .xp-choice-body button:hover{background:linear-gradient(#eaf5ff,#b9dcfa);border-color:#4c99df}
    .xp-choice-body button::first-line{font-size:28px}
    @media(max-width:560px){.xp-start-menu{left:3px;width:calc(100vw - 6px)}.start-body{grid-template-columns:minmax(0,1fr) 95px}.ai-launch{padding:6px}.start-side{padding:7px 5px}}
  `;
  document.head.appendChild(style);

  const startButton = document.querySelector(".xp-start");
  if (!startButton) return;
  startButton.id = "xpStartButton";
  startButton.setAttribute("aria-expanded", "false");
  startButton.setAttribute("aria-controls", "xpStartMenu");

  const menu = document.createElement("div");
  menu.id = "xpStartMenu";
  menu.className = "xp-start-menu";
  menu.hidden = true;
  menu.setAttribute("aria-label", "Menu Démarrer DIVINARVIS");

  const appButtons = APPS.map(([name, symbol, description, background]) => `
    <button class="ai-launch" data-ai="${name}">
      <span class="ai-icon" style="background:${background}">${symbol}</span>
      <span class="ai-copy"><strong>${name}</strong><small>${description}</small></span>
    </button>
  `).join("");

  menu.innerHTML = `
    <div class="start-profile"><div class="start-avatar">D</div><div><strong>DIVINARVIS</strong><small>AI Command Center • La famille</small></div></div>
    <div class="start-body"><div class="start-apps">${appButtons}</div><div class="start-side">
      <button data-local="home">🎵 Media Player</button><button data-local="library">📁 Bibliothèque</button><button data-local="radio">📻 Radios</button><button data-local="settings">⚙ Paramètres</button>
    </div></div>
    <div class="start-footer"><button id="closeStartMenu">✕ Fermer</button></div>
  `;
  document.body.appendChild(menu);

  const toast = document.createElement("div");
  toast.className = "start-toast";
  toast.setAttribute("role", "status");
  document.body.appendChild(toast);
  const notify = message => { toast.textContent = message; toast.classList.add("show"); clearTimeout(notify.timer); notify.timer = setTimeout(() => toast.classList.remove("show"), 2200); };
  const setMenu = open => { menu.hidden = !open; startButton.setAttribute("aria-expanded", String(open)); };
  const launchAI = (name, url = WEB_APPS[name]) => {
  setMenu(false);
  const popupName = `divinarvis_${name.replace(/[^a-z0-9]+/gi, "_")}`;
  const popup = window.open(url, popupName, POPUP_FEATURES);
  if (!popup) notify("Pop-up bloquée : autorise les fenêtres pour DIVINARVIS.");
  else { try { popup.focus(); } catch (_) {} }
};

const choice = document.createElement("div");
choice.className = "xp-choice";
choice.hidden = true;
document.body.appendChild(choice);

const openChoice = name => {
  setMenu(false);
  choice.innerHTML = `<div class="xp-choice-title"><span>${name}</span><button id="xpChoiceClose">✕</button></div><div class="xp-choice-body">${CHOICES[name].map(([icon, label, subtitle], i) => `<button data-i="${i}"><span style="font-size:32px;line-height:1">${icon}</span><strong>${label}</strong><small>${subtitle}</small></button>`).join("")}</div>`;
  choice.hidden = false;
  choice.querySelector("#xpChoiceClose").onclick = () => { choice.hidden = true; };
  choice.querySelectorAll("[data-i]").forEach(b => b.onclick = () => { choice.hidden = true; launchAI(name + " / " + CHOICES[name][b.dataset.i][1], CHOICES[name][b.dataset.i][3]); });
};

  startButton.addEventListener("click", event => { event.stopPropagation(); setMenu(menu.hidden); });
  menu.querySelector("#closeStartMenu").addEventListener("click", () => setMenu(false));
menu.querySelectorAll(".ai-launch").forEach(button => button.addEventListener("click", () => CHOICES[button.dataset.ai] ? openChoice(button.dataset.ai) : launchAI(button.dataset.ai)));  menu.querySelectorAll("[data-local]").forEach(button => button.addEventListener("click", () => { setMenu(false); if (typeof window.showPage === "function") window.showPage(button.dataset.local); }));
  document.addEventListener("click", event => { if (!menu.hidden && !menu.contains(event.target) && event.target !== startButton) setMenu(false); });
  document.addEventListener("keydown", event => { if (event.key === "Escape") setMenu(false); });
})();

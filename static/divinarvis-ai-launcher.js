"use strict";

(() => {
  const SHORTCUT_NAME = "DIVINARVIS AI LAUNCHER";
  const WEB_APPS = {
    "ChatGPT": "https://chatgpt.com/",
    "Copilot": "https://copilot.microsoft.com/",
    "Gemini": "https://gemini.google.com/",
    "Grok": "https://grok.com/",
    "Meta AI": "https://www.meta.ai/",
    "Claude": "https://claude.ai/"
  };

  const APPS = [
    ["ChatGPT", "C", "Création et raisonnement", "#159f88"],
    ["Copilot", "∞", "Tonton Microsoft", "linear-gradient(135deg,#53c9ff,#7857ff,#ef55b8)"],
    ["Gemini", "✦", "Univers Google", "linear-gradient(135deg,#4078ff,#a666e8)"],
    ["Grok", "𝕏", "Assistant xAI", "#111"],
    ["Meta AI", "M", "Assistant Meta", "#1677e8"],
    ["Claude", "A", "Assistant Anthropic", "#bd643d"]
  ];

  const style = document.createElement("style");
  style.textContent = `
    .xp-start{position:relative;z-index:1002}
    .xp-start-menu{position:fixed;left:6px;bottom:36px;z-index:1001;width:min(350px,calc(100vw - 12px));color:#35152c;border:2px solid #a62075;border-radius:8px 8px 0 0;overflow:hidden;background:#fff;box-shadow:5px -7px 24px rgba(78,11,55,.42);transform-origin:left bottom;transition:opacity .14s ease,transform .14s ease}
    .xp-start-menu[hidden]{display:block;opacity:0;transform:translateY(9px) scale(.97);pointer-events:none}
    .xp-start-menu:not([hidden]){opacity:1;transform:none}
    .start-profile{display:flex;align-items:center;gap:11px;padding:12px 14px;color:#fff;background:linear-gradient(#ff88c7,#d33892 48%,#a71e70);text-shadow:1px 1px #72124c}
    .start-avatar{width:40px;height:40px;border:2px solid #fff;border-radius:8px;display:grid;place-items:center;background:linear-gradient(135deg,#fff,#ffcbe7);color:#a71e70;font-size:22px;font-weight:900}
    .start-profile strong,.ai-copy strong,.ai-copy small{display:block}.start-profile small{opacity:.9}
    .start-body{display:grid;grid-template-columns:minmax(0,1fr) 112px}.start-apps{padding:7px;background:#fff}
    .ai-launch{width:100%;display:grid;grid-template-columns:38px minmax(0,1fr);align-items:center;gap:9px;padding:7px;border:1px solid transparent;border-radius:5px;color:#35152c;background:transparent;text-align:left;cursor:pointer}
    .ai-launch:hover,.ai-launch:focus{background:linear-gradient(90deg,#ffe1f1,#eedfff);border-color:#dd8dbf;outline:none}
    .ai-icon{width:36px;height:36px;border-radius:8px;display:grid;place-items:center;color:#fff;font-weight:900;font-size:17px;box-shadow:inset 0 1px rgba(255,255,255,.5),1px 2px 4px rgba(73,17,57,.2)}
    .ai-copy{min-width:0;width:100%;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;text-align:left;line-height:1.22}.ai-copy strong{width:100%;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ai-copy small{width:100%;color:#906a84;font-size:10px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .start-side{padding:9px 8px;background:linear-gradient(#f0def9,#dbe8ff);border-left:1px solid #d1add2}
    .start-side button{width:100%;border:0;background:transparent;color:#52223f;text-align:left;padding:8px 6px;border-radius:4px;font-size:11px;cursor:pointer}
    .start-side button:hover{background:rgba(255,255,255,.75)}
    .start-footer{display:flex;justify-content:flex-end;padding:8px 10px;background:linear-gradient(#e999c8,#c53d8a)}
    .start-footer button{border:1px solid rgba(255,255,255,.75);border-radius:4px;padding:5px 9px;color:#fff;background:rgba(111,22,79,.35);cursor:pointer}
    .start-toast{position:fixed;left:50%;bottom:50px;z-index:1200;transform:translateX(-50%);padding:9px 14px;border:2px solid #a62075;border-radius:7px;background:#fff6fc;color:#641747;box-shadow:0 5px 18px rgba(82,10,58,.3);font-weight:700;opacity:0;pointer-events:none;transition:.2s}
    .start-toast.show{opacity:1;bottom:57px}
    @media(max-width:560px){.xp-start-menu{left:3px;width:calc(100vw - 6px)}.start-body{grid-template-columns:minmax(0,1fr) 95px}.ai-launch{padding:6px}.start-side{padding:7px 5px}}
  `;
  document.head.appendChild(style);

  const startButton = document.querySelector(".xp-start");
  if (!startButton) {
    console.error("DIVINARVIS AI Launcher : bouton .xp-start introuvable.");
    return;
  }

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
    <div class="start-profile">
      <div class="start-avatar">D</div>
      <div><strong>DIVINARVIS</strong><small>AI Command Center</small></div>
    </div>
    <div class="start-body">
      <div class="start-apps">${appButtons}</div>
      <div class="start-side">
        <button data-local="home">🎵 Media Player</button>
        <button data-local="library">📁 Bibliothèque</button>
        <button data-local="radio">📻 Radios</button>
        <button data-local="settings">⚙ Paramètres</button>
        <button data-local="siri">🍎 Siri</button>
      </div>
    </div>
    <div class="start-footer"><button id="closeStartMenu">✕ Fermer</button></div>
  `;
  document.body.appendChild(menu);

  const toast = document.createElement("div");
  toast.className = "start-toast";
  toast.setAttribute("role", "status");
  document.body.appendChild(toast);

  const isAppleMobile = () => /iPhone|iPad|iPod/i.test(navigator.userAgent);
  const setMenu = open => {
    menu.hidden = !open;
    startButton.setAttribute("aria-expanded", String(open));
  };
  const notify = message => {
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(notify.timer);
    notify.timer = setTimeout(() => toast.classList.remove("show"), 1900);
  };
  const launchAI = name => {
    setMenu(false);
    if (isAppleMobile()) {
      notify(`Ouverture de ${name} via Raccourcis…`);
      location.href = `shortcuts://run-shortcut?name=${encodeURIComponent(SHORTCUT_NAME)}&input=text&text=${encodeURIComponent(name)}`;
      return;
    }
    notify(`Ouverture de ${name}…`);
    window.open(WEB_APPS[name], "_blank", "noopener,noreferrer");
  };

  startButton.addEventListener("click", event => {
    event.stopPropagation();
    setMenu(menu.hidden);
  });
  menu.querySelector("#closeStartMenu").addEventListener("click", () => setMenu(false));
  menu.querySelectorAll(".ai-launch").forEach(button => {
    button.addEventListener("click", () => launchAI(button.dataset.ai));
  });
  menu.querySelectorAll("[data-local]").forEach(button => {
    button.addEventListener("click", () => {
      const action = button.dataset.local;
      setMenu(false);
      if (action === "siri") {
        location.href = `shortcuts://open-shortcut?name=${encodeURIComponent("DIVINARVIS")}`;
      } else if (typeof window.showPage === "function") {
        window.showPage(action);
      }
    });
  });
  document.addEventListener("click", event => {
    if (!menu.hidden && !menu.contains(event.target) && event.target !== startButton) setMenu(false);
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape") setMenu(false);
  });
})();

"use strict";

/* DIVINARVIS V10 - Correctif final radios intégré
   - Capital & Capital XTRA : lecture directe dans le lecteur interne
   - Love Radio Russie : ouverture/fermeture du lecteur officiel dans un onglet externe
*/
(() => {
  const get = id => document.getElementById(id);
  const audio = get("audio");
  if (!audio) return;

  const capitalButton = get("capitalBtn");
  const capitalQuick = get("capitalQuick");
  const xtraButton = get("xtraBtn");
  const xtraQuick = get("xtraQuick");
  const loveButton = get("loveRadioBtn");
  const radioState = get("radioState");
  const statusTrack = get("statusTrack");

  let activeRadio = null; // "capital", "xtra" ou null
  let loveTab = null;

  const CAPITAL_STREAMS = [
    "https://media-ice.musicradio.com/CapitalUKMP3",
    "https://media-ssl.musicradio.com/Capital"
  ];
  const XTRA_STREAMS = [
    "https://media-ice.musicradio.com/CapitalXTRAUKMP3",
    "https://media-ssl.musicradio.com/CapitalXTRA"
  ];
  const LOVE_PLAYER = "https://player.loveradio.ru/";

  const oldLoveWindow = get("loveRadioWindow");
  if (oldLoveWindow) oldLoveWindow.remove();

  const setState = message => {
    if (radioState) radioState.textContent = message;
  };

  const setStatusTrack = message => {
    if (statusTrack) statusTrack.textContent = message;
  };

  const markButton = (button, active) => {
    if (!button) return;
    button.classList.toggle("radio-btn-on", active);
    button.setAttribute("aria-pressed", String(active));
  };

  const updateButtons = () => {
    const isPlaying = !audio.paused;
    markButton(capitalButton, activeRadio === "capital" && isPlaying);
    markButton(xtraButton, activeRadio === "xtra" && isPlaying);
    markButton(loveButton, Boolean(loveTab && !loveTab.closed));

    if (capitalButton) {
      capitalButton.textContent = (activeRadio === "capital" && isPlaying) ? "■ Capital" : "▶ Capital";
    }
    if (xtraButton) {
      xtraButton.textContent = (activeRadio === "xtra" && isPlaying) ? "■ XTRA" : "▶ XTRA";
    }
  };

  const stopRadio = () => {
    if (!activeRadio) return;
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    const oldName = activeRadio === "capital" ? "Capital" : "Capital XTRA";
    activeRadio = null;
    setState(`${oldName} arrêtée`);
    setStatusTrack("Aucun média");
    updateButtons();
  };

  const startRadioStream = async (name, streams) => {
    if (activeRadio) {
      audio.pause();
      audio.removeAttribute("src");
    }

    activeRadio = (name === "Capital") ? "capital" : "xtra";
    let position = 0;

    const attempt = async () => {
      if (!activeRadio) return;
      if (position >= streams.length) {
        activeRadio = null;
        setState(`${name} indisponible`);
        updateButtons();
        return;
      }

      audio.src = streams[position++];
      if (get("title")) get("title").textContent = name;
      if (get("meta")) get("meta").textContent = "Radio en direct";
      if (get("liveHint")) get("liveHint").textContent = "Flux radio";
      setState(`Connexion à ${name}...`);
      setStatusTrack(name);

      try {
        await audio.play();
        setState(`En direct : ${name} - appuie de nouveau pour arrêter`);
        updateButtons();
      } catch (_) {
        setTimeout(attempt, 450);
      }
    };

    await attempt();
  };

  const toggleInternalRadio = (name) => {
    const targetKey = (name === "Capital") ? "capital" : "xtra";
    if (activeRadio === targetKey && !audio.paused) {
      stopRadio();
    } else {
      const streams = (name === "Capital") ? CAPITAL_STREAMS : XTRA_STREAMS;
      startRadioStream(name, streams);
    }
  };

  const toggleLoveRadio = () => {
    if (loveTab && !loveTab.closed) {
      loveTab.close();
      loveTab = null;
      setState("Love Radio fermée");
      updateButtons();
      return;
    }

    stopRadio();
    loveTab = window.open(LOVE_PLAYER, "divinarvisLoveRadio");
    if (loveTab) {
      setState("Love Radio ouverte dans un nouvel onglet");
      setStatusTrack("Love Radio Russie");
    } else {
      setState("Le navigateur a bloqué l'onglet Love Radio");
    }
    updateButtons();
  };

  if (capitalButton) capitalButton.onclick = () => toggleInternalRadio("Capital");
  if (capitalQuick) capitalQuick.onclick = () => toggleInternalRadio("Capital");
  
  if (xtraButton) xtraButton.onclick = () => toggleInternalRadio("Capital XTRA");
  if (xtraQuick) xtraQuick.onclick = () => toggleInternalRadio("Capital XTRA");
  
  if (loveButton) loveButton.onclick = toggleLoveRadio;

  audio.addEventListener("pause", updateButtons);
  audio.addEventListener("play", updateButtons);

  const style = document.createElement("style");
  style.textContent = `
    .radio-btn-on {
      filter: brightness(1.12);
      box-shadow: inset 0 0 0 2px rgba(255,255,255,.9),
                  0 0 12px rgba(227,62,152,.45) !important;
    }
    .love-radio-btn.radio-btn-on {
      box-shadow: inset 0 0 0 2px #fff,
                  0 0 13px rgba(217,25,37,.58) !important;
    }
  `;
  document.head.appendChild(style);

  updateButtons();
})();

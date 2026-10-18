"use strict";

/* DIVINARVIS V10 - Correctif final radios
   - Capital : lecture/arret dans le lecteur principal
   - Capital XTRA : ouverture/fermeture du lecteur web dans un onglet
   - Love Radio Russie : ouverture/fermeture du lecteur officiel dans un onglet
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

  let capitalActive = false;
  let xtraTab = null;
  let loveTab = null;

  const CAPITAL_STREAMS = [
    "https://media-ice.musicradio.com/CapitalUKMP3",
    "https://media-ssl.musicradio.com/Capital"
  ];
  const XTRA_PLAYER = "https://play.radioplayer.org/en/live/ODI2fjEyNjg";
  const LOVE_PLAYER = "https://player.loveradio.ru/";

  // L'ancienne fenetre Love Radio n'est plus utilisee.
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
    markButton(capitalButton, capitalActive && !audio.paused);
    markButton(xtraButton, Boolean(xtraTab && !xtraTab.closed));
    markButton(loveButton, Boolean(loveTab && !loveTab.closed));

    if (capitalButton) {
      capitalButton.textContent = capitalActive && !audio.paused
        ? "■ Capital"
        : "▶ Capital";
    }
    if (xtraButton) {
      xtraButton.textContent = xtraTab && !xtraTab.closed
        ? "■ Capital XTRA"
        : "▶ Capital XTRA";
    }
  };

  const stopCapital = () => {
    if (!capitalActive) return;
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    capitalActive = false;
    setState("Capital arretee");
    setStatusTrack("Aucun media");
    updateButtons();
  };

  const startCapital = async () => {
    if (typeof window.closeLoveRadio === "function") {
      try { window.closeLoveRadio(); } catch (_) {}
    }

    capitalActive = true;
    let position = 0;

    const attempt = async () => {
      if (!capitalActive) return;
      if (position >= CAPITAL_STREAMS.length) {
        capitalActive = false;
        setState("Capital indisponible");
        updateButtons();
        return;
      }

      audio.src = CAPITAL_STREAMS[position++];
      if (get("title")) get("title").textContent = "Capital";
      if (get("meta")) get("meta").textContent = "Radio en direct";
      if (get("liveHint")) get("liveHint").textContent = "Flux radio";
      setState("Connexion a Capital...");
      setStatusTrack("Capital");

      try {
        await audio.play();
        setState("En direct : Capital - appuie de nouveau pour arreter");
        updateButtons();
      } catch (_) {
        setTimeout(attempt, 450);
      }
    };

    await attempt();
  };

  const toggleCapital = () => {
    if (capitalActive && !audio.paused) stopCapital();
    else startCapital();
  };

  const toggleExternalRadio = (kind) => {
    const isXtra = kind === "xtra";
    let tab = isXtra ? xtraTab : loveTab;
    const name = isXtra ? "Capital XTRA" : "Love Radio Russie";
    const url = isXtra ? XTRA_PLAYER : LOVE_PLAYER;
    const target = isXtra ? "divinarvisCapitalXtra" : "divinarvisLoveRadio";

    if (tab && !tab.closed) {
      tab.close();
      if (isXtra) xtraTab = null;
      else loveTab = null;
      setState(`${name} fermee`);
      updateButtons();
      return;
    }

    stopCapital();
    tab = window.open(url, target);
    if (isXtra) xtraTab = tab;
    else loveTab = tab;

    if (tab) {
      setState(`${name} ouverte dans un nouvel onglet - appuie de nouveau pour fermer`);
      setStatusTrack(name);
    } else {
      setState(`Le navigateur a bloque l'onglet ${name}`);
    }
    updateButtons();
  };

  if (capitalButton) capitalButton.onclick = toggleCapital;
  if (capitalQuick) capitalQuick.onclick = toggleCapital;
  if (xtraButton) xtraButton.onclick = () => toggleExternalRadio("xtra");
  if (xtraQuick) xtraQuick.onclick = () => toggleExternalRadio("xtra");
  if (loveButton) loveButton.onclick = () => toggleExternalRadio("love");

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

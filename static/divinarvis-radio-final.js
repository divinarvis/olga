"use strict";

/* DIVINARVIS V10 - radios robustes
   IMPORTANT : ce fichier doit etre charge APRES le script principal de index.html.
   Capital : audio interne ON/OFF.
   Capital XTRA : Radioplayer officiel/public dans un nouvel onglet.
   Love Radio : lecteur officiel dans un nouvel onglet.
*/
(() => {
  const $ = id => document.getElementById(id);
  const audio = $("audio");
  if (!audio) {
    console.error("DIVINARVIS RADIO: #audio introuvable");
    return;
  }

  const capitalBtn = $("capitalBtn");
  const capitalQuick = $("capitalQuick");
  const xtraBtn = $("xtraBtn");
  const xtraQuick = $("xtraQuick");
  const loveBtn = $("loveRadioBtn");
  const radioState = $("radioState");
  const statusTrack = $("statusTrack");
  const title = $("title");
  const meta = $("meta");
  const liveHint = $("liveHint");

  const CAPITAL_STREAMS = [
    "https://media-ice.musicradio.com/CapitalUKMP3",
    "https://media-ssl.musicradio.com/Capital"
  ];
  const XTRA_URL = "https://play.radioplayer.org/en/live/ODI2fjEyNjg";
  const LOVE_URL = "https://www.loveradio.ru/player/";

  let capitalOn = false;
  let xtraTab = null;
  let loveTab = null;
  let capitalAttempt = 0;

  function state(text) {
    if (radioState) radioState.textContent = text;
  }

  function status(text) {
    if (statusTrack) statusTrack.textContent = text;
  }

  function tabOpen(tab) {
    try { return Boolean(tab && !tab.closed); }
    catch (_) { return false; }
  }

  function decorate(button, active) {
    if (!button) return;
    button.classList.toggle("radio-btn-on", active);
    button.setAttribute("aria-pressed", String(active));
  }

  function refreshButtons() {
    const capitalPlaying = capitalOn && !audio.paused;
    decorate(capitalBtn, capitalPlaying);
    decorate(xtraBtn, tabOpen(xtraTab));
    decorate(loveBtn, tabOpen(loveTab));

    if (capitalBtn) capitalBtn.textContent = "Capital London";
    if (xtraBtn) xtraBtn.textContent = "Capital XTRA";
  }

  function clearInternalAudio() {
    capitalAttempt += 1; // annule toute tentative asynchrone precedente
    capitalOn = false;
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    refreshButtons();
  }

  function stopCapital() {
    clearInternalAudio();
    state("Capital arrÃªtÃ©e");
    status("Aucun mÃ©dia");
    if (typeof window.pushSync === "function") {
      window.pushSync("stopRadio", { currentRadioId: "capital" });
    }
  }

  async function startCapital() {
    // Ferme les onglets radios externes quand Capital prend la main.
    if (tabOpen(xtraTab)) { xtraTab.close(); xtraTab = null; }
    if (tabOpen(loveTab)) { loveTab.close(); loveTab = null; }

    clearInternalAudio();
    capitalOn = true;
    const attemptId = ++capitalAttempt;

    for (const stream of CAPITAL_STREAMS) {
      if (!capitalOn || attemptId !== capitalAttempt) return;

      audio.src = stream;
      if (title) title.textContent = "Capital";
      if (meta) meta.textContent = "Radio en direct";
      if (liveHint) liveHint.textContent = "Flux Capital";
      state("Connexion Ã  Capitalâ¦");
      status("Capital");

      try {
        await audio.play();
        if (!capitalOn || attemptId !== capitalAttempt) return;
        state("En direct : Capital â¢ retouche le bouton pour arrÃªter");
        refreshButtons();
        if (typeof window.pushSync === "function") {
          window.pushSync("capital", {
            capitalUrl: stream,
            capitalName: "Capital",
            currentRadioId: "capital",
            currentTime: 0
          });
        }
        return;
      } catch (error) {
        console.warn("DIVINARVIS RADIO: Ã©chec Capital", stream, error);
      }
    }

    capitalOn = false;
    state("Capital indisponible depuis ce navigateur");
    status("Aucun mÃ©dia");
    refreshButtons();
  }

  function toggleCapital() {
    if (capitalOn && !audio.paused) stopCapital();
    else startCapital();
  }

  function toggleExternal(kind) {
    const isXtra = kind === "xtra";
    const name = isXtra ? "Capital XTRA" : "Love Radio";
    const url = isXtra ? XTRA_URL : LOVE_URL;
    const target = isXtra ? "divinarvisCapitalXtra" : "divinarvisLoveRadio";
    let tab = isXtra ? xtraTab : loveTab;

    if (tabOpen(tab)) {
      tab.close();
      if (isXtra) xtraTab = null;
      else loveTab = null;
      state(`${name} fermÃ©e`);
      status("Aucun mÃ©dia");
      refreshButtons();
      return;
    }

    clearInternalAudio();

    // Doit rester directement dans le gestionnaire de clic pour Safari/iPhone.
    tab = window.open(url, target);
    if (isXtra) xtraTab = tab;
    else loveTab = tab;

    if (tab) {
      state(`${name} ouverte dans un nouvel onglet`);
      status(name);
      try { tab.focus(); } catch (_) {}
    } else {
      state(`Ouverture de ${name} bloquÃ©e par le navigateur`);
    }
    refreshButtons();
  }

  // onclick remplace proprement tout ancien handler du script principal.
  if (capitalBtn) capitalBtn.onclick = toggleCapital;
  if (capitalQuick) capitalQuick.onclick = toggleCapital;
  if (xtraBtn) xtraBtn.onclick = () => toggleExternal("xtra");
  if (xtraQuick) xtraQuick.onclick = () => toggleExternal("xtra");
  if (loveBtn) loveBtn.onclick = () => toggleExternal("love");

  audio.addEventListener("play", refreshButtons);
  audio.addEventListener("pause", refreshButtons);
  window.addEventListener("focus", refreshButtons);
  document.addEventListener("visibilitychange", refreshButtons);

  const css = document.createElement("style");
  css.textContent = `
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
  document.head.appendChild(css);

  refreshButtons();
  console.info("DIVINARVIS RADIO: module chargÃ©");
})();

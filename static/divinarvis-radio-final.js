bash -lc cat > /mnt/data/divinarvis-radio-final.js <<'JS'
"use strict";

/* DIVINARVIS V10 - RADIO FINAL
   - Capital : flux audio interne ON / OFF
   - Capital XTRA : lecteur web Radioplayer dans un nouvel onglet ON / OFF
   - Love Radio Russie : site officiel dans un nouvel onglet ON / OFF

   Pourquoi XTRA n'est plus lance avec les anciennes URL MP3 :
   le lecteur Radioplayer de Capital XTRA est publiquement disponible et evite
   de dependre d'anciennes adresses de flux direct qui peuvent changer.
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
  const title = get("title");
  const meta = get("meta");
  const liveHint = get("liveHint");

  let capitalActive = false;
  let xtraTab = null;
  let loveTab = null;

  const CAPITAL_STREAMS = [
    "https://media-ice.musicradio.com/CapitalUKMP3",
    "https://media-ssl.musicradio.com/Capital"
  ];

  // Lecteur web Capital XTRA verifie publiquement.
  const XTRA_URL = "https://play.radioplayer.org/en/live/ODI2fjEyNjg";
  const LOVE_URL = "https://www.loveradio.ru/";

  const setState = message => {
    if (radioState) radioState.textContent = message;
  };

  const setStatus = message => {
    if (statusTrack) statusTrack.textContent = message;
  };

  const markButton = (button, active) => {
    if (!button) return;
    button.classList.toggle("radio-btn-on", active);
    button.setAttribute("aria-pressed", String(active));
  };

  const updateButtons = () => {
    const capitalPlaying = capitalActive && !audio.paused;
    const xtraOpen = Boolean(xtraTab && !xtraTab.closed);
    const loveOpen = Boolean(loveTab && !loveTab.closed);

    markButton(capitalButton, capitalPlaying);
    markButton(xtraButton, xtraOpen);
    markButton(loveButton, loveOpen);

    if (capitalButton) {
      capitalButton.textContent = capitalPlaying ? "■ Capital" : "▶ Capital";
    }

    if (xtraButton) {
      xtraButton.textContent = xtraOpen ? "■ XTRA" : "▶ XTRA";
    }
  };

  const stopInternalAudio = () => {
    if (!capitalActive) return;
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    capitalActive = false;
    setState("Capital arrêtée");
    setStatus("Aucun média");
    updateButtons();

    if (typeof window.pushSync === "function") {
      window.pushSync("stopRadio", { currentRadioId: "capital" });
    }
  };

  const startCapital = async () => {
    // Le lecteur interne ne doit pas continuer si une autre radio est choisie.
    capitalActive = true;
    let position = 0;

    if (xtraTab && !xtraTab.closed) {
      xtraTab.close();
      xtraTab = null;
    }

    const attempt = async () => {
      if (!capitalActive) return;

      if (position >= CAPITAL_STREAMS.length) {
        capitalActive = false;
        setState("Capital indisponible");
        updateButtons();
        return;
      }

      const stream = CAPITAL_STREAMS[position++];
      audio.src = stream;

      if (title) title.textContent = "Capital";
      if (meta) meta.textContent = "Radio en direct";
      if (liveHint) liveHint.textContent = "Flux Capital";
      setState("Connexion à Capital…");
      setStatus("Capital");

      try {
        await audio.play();
        setState("En direct : Capital • appuie de nouveau pour arrêter");
        updateButtons();

        if (typeof window.pushSync === "function") {
          window.pushSync("capital", {
            capitalUrl: stream,
            capitalName: "Capital",
            currentRadioId: "capital",
            currentTime: 0
          });
        }
      } catch (_) {
        setTimeout(attempt, 450);
      }
    };

    await attempt();
  };

  const toggleCapital = () => {
    if (capitalActive && !audio.paused) stopInternalAudio();
    else startCapital();
  };

  const toggleXtra = () => {
    if (xtraTab && !xtraTab.closed) {
      xtraTab.close();
      xtraTab = null;
      setState("Capital XTRA fermée");
      setStatus("Aucun média");
      updateButtons();
      return;
    }

    stopInternalAudio();

    // window.open est execute directement dans le clic utilisateur afin que
    // Safari / iOS ait le moins de raisons possible de bloquer l'onglet.
    xtraTab = window.open(XTRA_URL, "divinarvisCapitalXtra");

    if (xtraTab) {
      setState("Capital XTRA ouverte dans Radioplayer • appuie de nouveau pour fermer");
      setStatus("Capital XTRA");
    } else {
      setState("Le navigateur a bloqué l'onglet Capital XTRA");
    }

    updateButtons();
  };

  const toggleLoveRadio = () => {
    if (loveTab && !loveTab.closed) {
      loveTab.close();
      loveTab = null;
      setState("Love Radio fermée");
      setStatus("Aucun média");
      updateButtons();
      return;
    }

    stopInternalAudio();
    loveTab = window.open(LOVE_URL, "divinarvisLoveRadio");

    if (loveTab) {
      setState("Love Radio ouverte dans un nouvel onglet • appuie de nouveau pour fermer");
      setStatus("Love Radio Russie");
    } else {
      setState("Le navigateur a bloqué l'ouverture de Love Radio");
    }

    updateButtons();
  };

  if (capitalButton) capitalButton.onclick = toggleCapital;
  if (capitalQuick) capitalQuick.onclick = toggleCapital;
  if (xtraButton) xtraButton.onclick = toggleXtra;
  if (xtraQuick) xtraQuick.onclick = toggleXtra;
  if (loveButton) loveButton.onclick = toggleLoveRadio;

  audio.addEventListener("play", updateButtons);
  audio.addEventListener("pause", updateButtons);

  // Quand l'utilisateur revient sur DIVINARVIS, recalcule l'etat des onglets.
  window.addEventListener("focus", updateButtons);
  document.addEventListener("visibilitychange", updateButtons);

  const style = document.createElement("style");
  style.textContent = `
    .radio-btn-on {
      filter: brightness(1.12);
      box-shadow:
        inset 0 0 0 2px rgba(255,255,255,.9),
        0 0 12px rgba(227,62,152,.45) !important;
    }
    .love-radio-btn.radio-btn-on {
      box-shadow:
        inset 0 0 0 2px #fff,
        0 0 13px rgba(217,25,37,.58) !important;
    }
  `;
  document.head.appendChild(style);

  updateButtons();
})();
JS
node --check /mnt/data/divinarvis-radio-final.js

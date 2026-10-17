/*
 * Banner cookie leggero + Google Analytics 4 con Consent Mode v2.
 * Nessun servizio esterno: GA4 viene scaricato SOLO dopo "Accetta".
 *
 * Uso:
 *   <link rel="stylesheet" href="/consenso/consenso-cookie.css">
 *   <script src="/consenso/consenso-cookie.js"
 *           data-ga-id="G-XXXXXXX"
 *           data-informativa="/cookie.html"
 *           data-logo="/logo/simbolo.svg"
 *           data-nome-sito="Nome sito"></script>
 * Per riaprire il banner: qualunque elemento con [data-preferenze-cookie]
 * oppure un link con href che termina in "#preferenze-cookie",
 * oppure window.ConsensoCookie.apri().
 * Opzionale: data-link-piede="selettore CSS" per aggiungere in automatico
 * il link "Preferenze cookie" accanto a quell'elemento (utile con SPA).
 */
(function () {
  'use strict';
  var script = document.currentScript;
  var cfg = {
    gaId: (script && script.getAttribute('data-ga-id')) || '',
    informativa: (script && script.getAttribute('data-informativa')) || '/cookie.html',
    logo: (script && script.getAttribute('data-logo')) || '',
    nome: (script && script.getAttribute('data-nome-sito')) || '',
    linkPiede: (script && script.getAttribute('data-link-piede')) || '',
    /* 'proprio' (default) = banner di questo modulo; 'iubenda' = nessun banner, si aggancia al consenso di iubenda */
    modalita: (script && script.getAttribute('data-modalita')) || 'proprio'
  };
  var CHIAVE = 'consenso-cookie-v1';
  var idValido = /^G-[A-Z0-9]{6,}$/.test(cfg.gaId) && cfg.gaId !== 'G-XXXXXXX';

  /* Consent Mode v2: tutto negato di default, prima di qualsiasi altra cosa */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;
  gtag('consent', 'default', {
    ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied',
    analytics_storage: 'denied', functionality_storage: 'denied',
    personalization_storage: 'denied', security_storage: 'granted',
    wait_for_update: 500
  });
  gtag('set', 'ads_data_redaction', true);

  function leggi() {
    try { var v = JSON.parse(localStorage.getItem(CHIAVE)); return v && (v.scelta === 'accettato' || v.scelta === 'rifiutato') ? v : null; }
    catch (e) { return null; }
  }
  function salva(scelta) {
    try { localStorage.setItem(CHIAVE, JSON.stringify({ scelta: scelta, data: new Date().toISOString() })); } catch (e) {}
  }

  var gaCaricato = false;
  function caricaGA(daIubenda) {
    if (gaCaricato || !idValido) return;
    gaCaricato = true;
    if (!daIubenda) gtag('consent', 'update', { analytics_storage: 'granted' });
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(cfg.gaId);
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', cfg.gaId, { anonymize_ip: true, allow_google_signals: false, allow_ad_personalization_signals: false });
  }

  function cancellaCookieGA() {
    var nomi = document.cookie.split(';').map(function (c) { return c.split('=')[0].trim(); })
      .filter(function (n) { return n === '_ga' || n.indexOf('_ga_') === 0 || n === '_gid'; });
    var host = location.hostname.split('.');
    var domini = [''];
    for (var i = 0; i < host.length - 1; i++) domini.push('; domain=.' + host.slice(i).join('.'));
    nomi.forEach(function (n) {
      domini.forEach(function (d) { document.cookie = n + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + d; });
    });
  }

  var banner = null;
  function crea() {
    if (banner) return banner;
    banner = document.createElement('div');
    banner.className = 'cc-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-live', 'polite');
    banner.setAttribute('aria-label', 'Preferenze cookie');
    banner.hidden = true;
    banner.innerHTML =
      '<div class="cc-contenuto">' +
        (cfg.logo ? '<img class="cc-logo" src="' + cfg.logo + '" alt="" width="40" height="40">' : '') +
        '<p class="cc-testo">Usiamo cookie tecnici necessari al funzionamento del sito. ' +
        'Con il tuo consenso useremmo anche Google Analytics per misurare in forma aggregata e con IP anonimizzato le visite' +
        (cfg.nome ? ' a ' + cfg.nome : '') + '. Puoi cambiare idea in qualsiasi momento da «Preferenze cookie» in fondo alla pagina. ' +
        '<a href="' + cfg.informativa + '">Leggi la cookie policy</a>.</p>' +
        '<div class="cc-pulsanti">' +
          '<button type="button" class="cc-btn" data-cc="rifiutato">Rifiuta</button>' +
          '<button type="button" class="cc-btn" data-cc="accettato">Accetta</button>' +
        '</div>' +
      '</div>';
    banner.addEventListener('click', function (e) {
      var b = e.target.closest('[data-cc]');
      if (!b) return;
      var scelta = b.getAttribute('data-cc');
      var prima = leggi();
      salva(scelta);
      chiudi();
      if (scelta === 'accettato') caricaGA();
      else {
        gtag('consent', 'update', { analytics_storage: 'denied' });
        cancellaCookieGA();
        /* se GA era già attivo in questa pagina, ricarico per scaricarlo del tutto */
        if (gaCaricato || (prima && prima.scelta === 'accettato')) location.reload();
      }
    });
    document.body.appendChild(banner);
    return banner;
  }
  function apri() { crea().hidden = false; }
  function chiudi() { if (banner) banner.hidden = true; }

  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('[data-preferenze-cookie], a[href$="#preferenze-cookie"]');
    if (!el) return;
    e.preventDefault();
    apri();
  });

  function aggiungiLinkPiede() {
    if (!cfg.linkPiede || document.querySelector('[data-preferenze-cookie]')) return;
    var rif = document.querySelector(cfg.linkPiede);
    if (!rif) return;
    var a = document.createElement('a');
    a.href = '#preferenze-cookie';
    a.setAttribute('data-preferenze-cookie', '');
    a.className = rif.className;
    a.textContent = 'Preferenze cookie';
    rif.insertAdjacentElement('afterend', a);
    if (rif.parentNode && rif.parentNode.tagName === 'LI') {
      var li = document.createElement('li');
      li.className = rif.parentNode.className;
      rif.parentNode.insertAdjacentElement('afterend', li);
      li.appendChild(a);
    }
  }

  function agganciaIubenda() {
    function controlla(a) {
      if (a && a[0] === 'consent' && a[1] === 'update' && a[2] && a[2].analytics_storage === 'granted') caricaGA(true);
    }
    for (var i = 0; i < window.dataLayer.length; i++) controlla(window.dataLayer[i]);
    var push = window.dataLayer.push;
    window.dataLayer.push = function () {
      for (var j = 0; j < arguments.length; j++) controlla(arguments[j]);
      return push.apply(window.dataLayer, arguments);
    };
  }
  if (cfg.modalita === 'iubenda') {
    agganciaIubenda();
    window.ConsensoCookie = { modalita: 'iubenda', gaCaricato: function () { return gaCaricato; } };
    return;
  }

  function avvio() {
    var v = leggi();
    if (v && v.scelta === 'accettato') caricaGA();
    else if (!v) apri();
    if (location.hash === '#preferenze-cookie') apri();
    if (cfg.linkPiede) {
      aggiungiLinkPiede();
      new MutationObserver(aggiungiLinkPiede).observe(document.body, { childList: true, subtree: true });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', avvio); else avvio();

  window.ConsensoCookie = { apri: apri, stato: function () { var v = leggi(); return v ? v.scelta : null; } };
})();

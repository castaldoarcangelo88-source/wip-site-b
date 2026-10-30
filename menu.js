/* Menu in alto: su telefono diventa un pulsante hamburger (senza JS il menu resta sempre visibile). */
(function () {
  var nav = document.getElementById("menu-sito");
  if (!nav) return;
  var pulsante = nav.querySelector(".menu-pulsante"), elenco = nav.querySelector("ul");
  if (!pulsante || !elenco) return;
  var stretto = window.matchMedia("(max-width: 820px)");
  nav.classList.add("menu-js");
  function imposta(aperto) {
    nav.classList.toggle("aperto", aperto);
    pulsante.setAttribute("aria-expanded", aperto ? "true" : "false");
  }
  pulsante.addEventListener("click", function () { imposta(pulsante.getAttribute("aria-expanded") !== "true"); });
  nav.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && pulsante.getAttribute("aria-expanded") === "true") { imposta(false); pulsante.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (!nav.contains(e.target) && pulsante.getAttribute("aria-expanded") === "true") imposta(false);
  });
  function allarga() { if (!stretto.matches) imposta(false); }
  if (stretto.addEventListener) stretto.addEventListener("change", allarga); else stretto.addListener(allarga);
})();

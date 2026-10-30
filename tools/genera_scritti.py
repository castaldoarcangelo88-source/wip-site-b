#!/usr/bin/env python3
"""Rigenera una parte del sito dai dati in dati/:
 - scritti-da-manilla.html (articoli scritti da Manilla per altri siti) da dati/scritti-da-manilla.json
Per aggiungere una voce: aggiungi una riga al JSON (data AAAA-MM-GG oppure "" se non confermata)
e lancia: python3 tools/genera_scritti.py"""
import json, html, re, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
SITO = "https://ilmondodibabypepita.it/"
MESI = "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()
e = lambda s: html.escape(s, quote=True)
def data_it(d):
    a, m, g = d.split("-"); return f"{int(g)} {MESI[int(m)-1]} {a}"
def ordina(v): return sorted(v, key=lambda x: x["data"] or "0", reverse=True)

def scheda(testata, titolo, data, sintesi, url, dettaglio=""):
    t = f'<p class="scheda-articolo-testata">{e(testata)}</p>'
    if dettaglio: t += f'\n          <p class="scheda-articolo-data">{e(dettaglio)}</p>'
    d = f'\n          <p class="scheda-articolo-data"><time datetime="{data}">{data_it(data)}</time></p>' if data else ""
    s = f'\n          <p class="scheda-articolo-sintesi">{e(sintesi)}</p>' if sintesi else ""
    return f'''        <li class="scheda-articolo">
          {t}
          <h4>{e(titolo)}</h4>{d}{s}
          <p class="voce-link"><a href="{e(url)}" target="_blank" rel="noopener">Leggi l'articolo</a></p>
        </li>'''

# --- pagina «Articoli scritti da Manilla»
scr = ordina(json.loads((R/"dati/scritti-da-manilla.json").read_text()))
URL = SITO + "scritti-da-manilla.html"
DESC = ("Gli articoli scritti da Manilla Castaldo per altri siti e giornali: Appunti di Zelda, Alleanza Cattolica "
        "e La Fragola Napoli News.")
items = [{"@type": "ListItem", "position": i+1, "item": {"@type": "Article", "headline": x["titolo"], "url": x["url"],
          "author": {"@id": SITO+"#manilla"}, "publisher": {"@type": "Organization", "name": x["testata"]},
          **({"datePublished": x["data"]} if x["data"] else {})}} for i, x in enumerate(scr)]
ld = {"@context": "https://schema.org", "@graph": [
  {"@type": "Person", "@id": SITO+"#manilla", "name": "Manilla", "url": SITO, "image": SITO+"assets/manilla.webp"},
  {"@type": "CollectionPage", "@id": URL+"#pagina", "url": URL, "name": "Articoli scritti da Manilla", "description": DESC,
   "inLanguage": "it", "isPartOf": {"@type": "WebSite", "name": "Il Mondo di Baby Pepita", "url": SITO},
   "about": {"@id": SITO+"#manilla"},
   "mainEntity": {"@type": "ItemList", "name": "Articoli scritti da Manilla", "numberOfItems": len(scr), "itemListElement": items}}]}
schede = "\n".join(scheda(x["testata"], x["titolo"], x["data"], x.get("sintesi"), x["url"]) for x in scr)
pagina = f'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Articoli scritti da Manilla · Il Mondo di Baby Pepita</title>
<meta name="description" content="{e(DESC)}">
<link rel="canonical" href="{URL}">
<meta property="og:type" content="website">
<meta property="og:locale" content="it_IT">
<meta property="og:site_name" content="Il Mondo di Baby Pepita">
<meta property="og:title" content="Articoli scritti da Manilla · Il Mondo di Baby Pepita">
<meta property="og:description" content="{e(DESC)}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="{SITO}assets/manilla.webp">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
<link rel="stylesheet" href="fonts/fonts.css">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="stylesheet" href="style.css?v=17">
<link rel="stylesheet" href="consenso/consenso-cookie.css">
<script src="consenso/consenso-cookie.js" data-ga-id="G-HYYZ6MDRPR" data-informativa="cookie.html" data-nome-sito="Il Mondo di Baby Pepita"></script>
</head>
<body class="pagina pagina-premi">
<header class="testata"><a href="./">Il Mondo di <span>Baby Pepita</span></a></header>
<main>
<section class="premi-intro">
  <h1 class="titolo-pagina">Articoli scritti da Manilla</h1>
  <div class="fregio" aria-hidden="true">✦ ❀ ✦</div>
  <p class="premi-sottotitolo">Gli articoli firmati da Manilla e pubblicati su altri siti e giornali</p>
</section>
<div class="linea-tempo">
  <section class="anno" id="articoli" aria-labelledby="titolo-articoli">
    <h2 class="anno-titolo" id="titolo-articoli">Gli articoli</h2>
    <!-- Schede generate da dati/scritti-da-manilla.json con tools/genera_scritti.py: non modificare a mano -->
    <ul class="schede-articoli">
{schede}
    </ul>
  </section>
</div>
<p class="nota"><a class="btn-opere" href="interviste-articoli.html">Interviste e articoli su Manilla</a> <a class="btn-opere" href="blog.html">Il blog di Manilla</a> <a class="btn-opere" href="./">Torna alla home</a></p>
</main>
<footer>© 2026 Il Mondo di Baby Pepita · ilmondodibabypepita.it · fatto con ♥ per Manilla<br><a class="piede-link" href="https://www.devsharesrl.it/contatti/">Contatti (DevShare SRL)</a> · <a class="piede-link" href="cookie.html">Cookie policy</a> · <a class="piede-link" href="#preferenze-cookie" data-preferenze-cookie>Preferenze cookie</a></footer>
</body>
</html>
'''
(R/"scritti-da-manilla.html").write_text(pagina)

print("ok:", len(scr), "articoli scritti")

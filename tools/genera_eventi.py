#!/usr/bin/env python3
"""Rigenera «Incontri ed eventi» da dati/eventi.json:
- incontri-eventi.html (griglia di riquadri, dal più recente)
- eventi/<id>.html (una pagina di dettaglio per evento con tutte le foto)
- il breve rimando in index.html (tra <!-- EVENTI --> e <!-- /EVENTI -->)
Per aggiungere un evento: aggiungi una voce al JSON (id, data AAAA-MM-GG, titolo, luogo, indirizzo,
citta, testo, foto[] con src/alt/width/height; la prima foto è la copertina; per ogni foto metti in
assets/eventi/ anche la versione piccola NOME-640.webp), lancia: python3 tools/genera_eventi.py
e aggiungi le nuove pagine a sitemap.xml."""
import json, html, re, pathlib, datetime
R = pathlib.Path(__file__).resolve().parent.parent
SITO = "https://ilmondodibabypepita.it/"
CSS = "16"
MESI = "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()
ev = sorted(json.loads((R/"dati/eventi.json").read_text()), key=lambda x: x["data"], reverse=True)
e = lambda s: html.escape(s, quote=False)
a = lambda s: html.escape(s)
def data_it(d):
    g = datetime.date.fromisoformat(d); return f"{g.day} {MESI[g.month-1]} {g.year}"
def luogo(x): return ", ".join(v for v in (x["luogo"], x["indirizzo"], x["citta"]) if v)
def piccola(f): return f["src"].rsplit(".", 1)[0] + "-640.webp"
def lato640(f): return round(f["width"]*640/max(f["width"], f["height"]))
def paragrafi(t): return [p.strip() for p in t.split("\n\n") if p.strip()]
def anteprima(x):  # prime due frasi/righe del testo, senza hashtag
    righe = [r for r in re.split(r"\n+", x["testo"]) if r.strip() and not r.strip().startswith("#")]
    return " ".join(righe[:2])
def descrizione(x):
    s = f"{x['titolo']}: {data_it(x['data'])}, {luogo(x)}. Le foto dell'incontro in cui Manilla ha raccontato HandiMap."
    return s

def testa(titolo, desc, url, img, ld, pre):
    return f'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titolo)}</title>
<meta name="description" content="{a(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="it_IT">
<meta property="og:site_name" content="Il Mondo di Baby Pepita">
<meta property="og:title" content="{a(titolo)}">
<meta property="og:description" content="{a(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
<link rel="stylesheet" href="{pre}fonts/fonts.css">
<link rel="icon" href="{pre}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{pre}favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="{pre}favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="{pre}apple-touch-icon.png">
<link rel="stylesheet" href="{pre}style.css?v={CSS}">
<link rel="stylesheet" href="{pre}consenso/consenso-cookie.css">
<script src="{pre}consenso/consenso-cookie.js" data-ga-id="G-HYYZ6MDRPR" data-informativa="{pre}cookie.html" data-nome-sito="Il Mondo di Baby Pepita"></script>
</head>
<body class="pagina pagina-premi pagina-eventi">
<header class="testata"><a href="{pre or './'}">Il Mondo di <span>Baby Pepita</span></a></header>
<main>
'''
def piede(pre):
    return f'''</main>
<footer>© 2026 Il Mondo di Baby Pepita · ilmondodibabypepita.it · fatto con ♥ per Manilla<br><a class="piede-link" href="https://www.devsharesrl.it/contatti/">Contatti (DevShare SRL)</a> · <a class="piede-link" href="{pre}incontri-eventi.html">Incontri ed eventi</a> · <a class="piede-link" href="{pre}cookie.html">Cookie policy</a> · <a class="piede-link" href="#preferenze-cookie" data-preferenze-cookie>Preferenze cookie</a></footer>
</body>
</html>
'''
PERSONA = {"@type": "Person", "@id": SITO+"#manilla", "name": "Manilla", "url": SITO, "image": SITO+"assets/manilla.webp"}
def evento_ld(x):
    return {"@type": "Event", "@id": SITO+f"eventi/{x['id']}.html#evento", "name": x["titolo"], "url": SITO+f"eventi/{x['id']}.html",
      "startDate": x["data"], "eventStatus": "https://schema.org/EventScheduled",
      "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
      "location": {"@type": "Place", "name": x["luogo"], "address": {"@type": "PostalAddress",
        **({"streetAddress": x["indirizzo"]} if x["indirizzo"] else {}), "addressLocality": x["citta"], "addressCountry": "IT"}},
      "image": [SITO+f["src"] for f in x["foto"]], "description": anteprima(x),
      "performer": {"@id": SITO+"#manilla"}, "organizer": {"@id": SITO+"#manilla"}}

# --- griglia ---
def riquadro(x):
    f = x["foto"][0]
    return f'''    <li class="riquadro-evento">
      <a href="eventi/{x["id"]}.html">
        <img src="{piccola(f)}" srcset="{piccola(f)} {lato640(f)}w, {f["src"]} {f["width"]}w" sizes="(max-width: 699px) 92vw, 360px" alt="{a(f["alt"])}" width="{f["width"]}" height="{f["height"]}" loading="lazy" decoding="async">
        <span class="riquadro-testo">
          <span class="evento-data"><time datetime="{x["data"]}">{data_it(x["data"])}</time></span>
          <span class="riquadro-titolo">{e(x["titolo"])}</span>
          <span class="evento-luogo">{e(luogo(x))}</span>
          <span class="riquadro-anteprima">{e(anteprima(x))}</span>
          <span class="riquadro-cta">Guarda le foto →</span>
        </span>
      </a>
    </li>'''
DESC_G = "Gli incontri e gli eventi in cui Manilla ha raccontato HandiMap, il progetto per città più accessibili: " + "; ".join(f"{x['titolo']} ({data_it(x['data'])})" for x in ev) + "."
URL_G = SITO+"incontri-eventi.html"
ld_g = {"@context": "https://schema.org", "@graph": [PERSONA, {"@type": "CollectionPage", "@id": URL_G+"#pagina", "url": URL_G,
  "name": "Incontri ed eventi", "description": DESC_G, "inLanguage": "it",
  "isPartOf": {"@type": "WebSite", "name": "Il Mondo di Baby Pepita", "url": SITO}, "about": {"@id": SITO+"#manilla"},
  "mainEntity": {"@type": "ItemList", "name": "Incontri ed eventi di HandiMap", "numberOfItems": len(ev),
    "itemListElement": [{"@type": "ListItem", "position": i+1, "url": SITO+f"eventi/{x['id']}.html", "name": x["titolo"]} for i, x in enumerate(ev)]}},
  *[evento_ld(x) for x in ev]]}
g = testa("Incontri ed eventi · Il Mondo di Baby Pepita", DESC_G, URL_G, SITO+ev[0]["foto"][0]["src"], ld_g, "")
g += '''<section class="premi-intro">
  <h1 class="titolo-pagina">Incontri ed eventi</h1>
  <div class="fregio" aria-hidden="true">✦ ❀ ✦</div>
  <p class="premi-sottotitolo">Dove Manilla ha raccontato HandiMap</p>
</section>
<!-- Pagina generata da dati/eventi.json con tools/genera_eventi.py: non modificare a mano -->
<ul class="griglia-eventi">
''' + "\n".join(riquadro(x) for x in ev) + '''
</ul>
<p class="nota"><a class="btn-opere" href="https://handimap.it" target="_blank" rel="noopener">Scopri HandiMap</a> <a class="btn-opere" href="./">Torna alla home</a></p>
''' + piede("")
(R/"incontri-eventi.html").write_text(g)

# --- dettagli ---
(R/"eventi").mkdir(exist_ok=True)
for x in ev:
    url = SITO+f"eventi/{x['id']}.html"
    ld = {"@context": "https://schema.org", "@graph": [PERSONA, {**evento_ld(x), "description": x["testo"]},
      {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITO},
        {"@type": "ListItem", "position": 2, "name": "Incontri ed eventi", "item": URL_G},
        {"@type": "ListItem", "position": 3, "name": x["titolo"], "item": url}]}]}
    par = "\n".join(f"  <p>{e(p).replace(chr(10), '<br>')}</p>" for p in paragrafi(x["testo"]))
    foto = "\n".join(f'''  <li><a href="../{f["src"]}"><img src="../{piccola(f)}" srcset="../{piccola(f)} {lato640(f)}w, ../{f["src"]} {f["width"]}w" sizes="(max-width: 699px) 46vw, 240px" alt="{a(f["alt"])}" width="{f["width"]}" height="{f["height"]}" loading="lazy" decoding="async"></a></li>''' for f in x["foto"])
    d = testa(f"{x['titolo']} · Incontri ed eventi", descrizione(x), url, SITO+x["foto"][0]["src"], ld, "../")
    d += f'''<nav class="briciole" aria-label="Percorso"><a href="../">Home</a> › <a href="../incontri-eventi.html">Incontri ed eventi</a></nav>
<article class="dettaglio-evento" aria-labelledby="titolo-evento">
<section class="premi-intro">
  <p class="evento-data"><time datetime="{x["data"]}">{data_it(x["data"])}</time></p>
  <h1 class="titolo-pagina" id="titolo-evento">{e(x["titolo"])}</h1>
  <div class="fregio" aria-hidden="true">✦ ❀ ✦</div>
  <p class="premi-sottotitolo">{e(luogo(x))}</p>
</section>
<div class="dettaglio-testo">
{par}
</div>
<ul class="dettaglio-foto" aria-label="Foto dell'evento">
{foto}
</ul>
</article>
<p class="nota"><a class="btn-opere" href="../incontri-eventi.html">Tutti gli incontri</a> <a class="btn-opere" href="../">Torna alla home</a></p>
''' + piede("../")
    (R/f"eventi/{x['id']}.html").write_text(d)

# --- rimando in home ---
rim = '''    <p class="eventi-rimando">Le foto e i racconti degli incontri in cui Manilla ha presentato HandiMap, dalla Fiera EST di Napoli al Centro Ippico di Santa Maria Capua Vetere.</p>
    <a class="btn-opere" href="incontri-eventi.html">Guarda gli incontri</a>'''
p = R/"index.html"; t = p.read_text()
t = re.sub(r"(<!-- EVENTI -->).*?(<!-- /EVENTI -->)", lambda m: m.group(1)+"\n"+rim+"\n    "+m.group(2), t, flags=re.S)
t = re.sub(r"\n?<!-- EVENTI-JSONLD -->.*?<!-- /EVENTI-JSONLD -->", "", t, flags=re.S)
p.write_text(t); print("ok,", len(ev), "eventi")

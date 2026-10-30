#!/usr/bin/env python3
"""Rigenera le schede di articoli-interviste-libri.html (sezioni labirinti, oltre, premi) e
articoli-interviste-handimap.html (sezione handimap) da dati/articoli.json.
Per aggiungere un articolo: aggiungi una voce al JSON (sezione: labirinti, oltre, premi, handimap;
data AAAA-MM-GG oppure "" se non confermata) e lancia: python3 tools/genera_articoli.py"""
import json, html, re, pathlib, sys
R = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R/"tools"))
import menu
MESI = "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()
art = json.loads((R/"dati/articoli.json").read_text())
e = lambda s: html.escape(s, quote=True)
def data_it(d):
    a, m, g = d.split("-"); return f"{int(g)} {MESI[int(m)-1]} {a}"
def schede(sez):
    out = ['      <ul class="schede-articoli">']
    for x in sorted([x for x in art if x["sezione"] == sez], key=lambda x: x["data"] or "0", reverse=True):
        d = f'\n          <p class="scheda-articolo-data"><time datetime="{x["data"]}">{data_it(x["data"])}</time></p>' if x["data"] else ""
        s = f'\n          <p class="scheda-articolo-sintesi">{e(x["sintesi"])}</p>' if x.get("sintesi") else ""
        out.append(f'''        <li class="scheda-articolo">
          <p class="scheda-articolo-testata">{e(x["testata"])}</p>
          <h4>{e(x["titolo"])}</h4>{d}{s}
          <p class="voce-link"><a href="{e(x["url"])}" target="_blank" rel="noopener">{e(x.get("etichetta","Leggi l'articolo"))}</a></p>
        </li>''')
    out.append('      </ul>')
    return "\n".join(out)
PAGINE = {  # file -> (sezioni mostrate, nome della lista nel JSON-LD)
    "articoli-interviste-libri.html": (("labirinti", "oltre", "premi"), "Articoli e interviste tra libri e vita"),
    "articoli-interviste-handimap.html": (("handimap",), "Articoli e interviste su HandiMap"),
}
for fn, (sezioni, nome) in PAGINE.items():
    p = R/fn; t = p.read_text()
    for sez in sezioni:
        t = re.sub(rf"(<!-- ARTICOLI:{sez} -->).*?(<!-- /ARTICOLI:{sez} -->)", lambda m: m.group(1)+"\n"+schede(sez)+"\n      "+m.group(2), t, flags=re.S)
    uniche = list({x["url"]: x for x in art if x["sezione"] in sezioni}.values())
    items = [{"@type": "ListItem", "position": i+1, "item": {"@type": x.get("tipo") == "scheda" and "WebPage" or "Article", "headline": x["titolo"], "url": x["url"],
              "publisher": {"@type": "Organization", "name": x["testata"]}, **({"datePublished": x["data"]} if x["data"] else {}),
              "about": {"@id": "https://ilmondodibabypepita.it/#manilla"}}} for i, x in enumerate(uniche)]
    lista = {"@type": "ItemList", "name": nome, "numberOfItems": len(uniche), "itemListElement": items}
    t = re.sub(r'("about": \{"@id": "https://ilmondodibabypepita.it/#manilla"\})(,\n   "mainEntity": .*?)?\n  \}\n \]',
               lambda m: m.group(1)+',\n   "mainEntity": '+json.dumps(lista, ensure_ascii=False)+'\n  }\n ]', t, count=1, flags=re.S)
    p.write_text(menu.applica(t, fn))
    print(fn, "ok,", len(uniche), "articoli")

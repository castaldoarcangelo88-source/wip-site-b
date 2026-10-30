#!/usr/bin/env python3
"""Menu in alto del sito: unica fonte per tutte le pagine.
- applica(html, percorso): inserisce (o aggiorna) il menu in una pagina HTML; i generatori lo chiamano prima di scrivere.
- python3 tools/menu.py: applica il menu a tutte le pagine principali (cartella principale e blog/),
  escluse admin, le pagine-ponte WordPress (cartelle degli anni), le pagine con noindex e il vecchio indirizzo interviste-articoli.html.
Per aggiungere o rinominare una voce modifica VOCI e rilancia questo script."""
import re, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
CSS_VER = "18"
# (chiave, etichetta, file)
VOCI = [
    ("home", "Home", "./"),
    ("opere", "Poesie e opere", "opere.html"),
    ("libri", "I libri di Manilla", "libri.html"),
    ("antologie", "Le antologie", "antologie.html"),
    ("premi", "Premi e riconoscimenti", "premi.html"),
    ("presentazioni", "Presentazioni dei libri", "presentazioni.html"),
    ("art-libri", "Articoli e interviste tra libri e vita", "articoli-interviste-libri.html"),
    ("art-handimap", "Articoli e interviste su HandiMap", "articoli-interviste-handimap.html"),
    ("scritti", "Scritti da Manilla", "scritti-da-manilla.html"),
    ("blog", "Il blog di Manilla", "blog.html"),
]
PAGINA = {"index.html": "home", "opere.html": "opere", "libri.html": "libri", "antologie.html": "antologie", "premi.html": "premi",
          "presentazioni.html": "presentazioni", "articoli-interviste-libri.html": "art-libri",
          "articoli-interviste-handimap.html": "art-handimap", "scritti-da-manilla.html": "scritti", "blog.html": "blog"}
SOTTOPAGINA = {"poesia.html": "opere"}   # pagine che appartengono a una voce: la voce risulta evidenziata
SALTA = {"interviste-articoli.html"}
RE_BLOCCO = re.compile(r"[ \t]*<!-- MENU -->.*?<!-- /MENU -->\n?", re.S)

def blocco(percorso):
    prefisso = "../" if percorso.startswith("blog/") else ""
    if percorso in PAGINA: chiave, esatta = PAGINA[percorso], True
    elif percorso in SOTTOPAGINA: chiave, esatta = SOTTOPAGINA[percorso], False
    elif percorso.startswith("blog/"): chiave, esatta = "blog", False
    else: chiave, esatta = None, False
    voci = []
    for k, etichetta, file in VOCI:
        href = (prefisso + file) if file != "./" else (prefisso or "./")
        corrente = ""
        if k == chiave: corrente = ' aria-current="page"' if esatta else ' aria-current="true"'
        voci.append(f'    <li><a href="{href}"{corrente}>{etichetta}</a></li>')
    return ('<!-- MENU -->\n<nav class="menu-sito" id="menu-sito" aria-label="Menu principale">\n'
            '  <button class="menu-pulsante" type="button" aria-expanded="false" aria-controls="menu-elenco"><span class="menu-icona" aria-hidden="true"></span><span>Menu</span></button>\n'
            '  <ul id="menu-elenco">\n' + "\n".join(voci) + '\n  </ul>\n'
            f'  <script src="{prefisso}menu.js" defer></script>\n</nav>\n<!-- /MENU -->\n')

def applica(html, percorso):
    """Restituisce la pagina con il menu aggiornato (invariata se ha noindex o non è una pagina principale)."""
    if percorso in SALTA or re.search(r"noindex", html, re.I): return html
    html = re.sub(r"style\.css\?v=\d+", f"style.css?v={CSS_VER}", html)
    html = RE_BLOCCO.sub("", html)
    b = blocco(percorso)
    m = re.search(r'<header class="testata">.*?</header>\n?', html, re.S)
    if m: return html[:m.end()] + b + html[m.end():]
    m = re.search(r'<div class="coriandoli" aria-hidden="true"></div>\n?', html)
    if m: return html[:m.end()] + b + html[m.end():]
    return html

def applica_tutto():
    n = 0
    for p in sorted(list(R.glob("*.html")) + list((R/"blog").glob("*.html"))):
        rel = p.relative_to(R).as_posix()
        t = p.read_text(); nuovo = applica(t, rel)
        if nuovo != t: p.write_text(nuovo); n += 1
    return n

if __name__ == "__main__":
    print("menu aggiornato in", applica_tutto(), "pagine")

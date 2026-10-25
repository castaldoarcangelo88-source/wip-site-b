#!/usr/bin/env python3
"""Rigenera «Incontri ed eventi» (sotto il link HandiMap in index.html) da dati/eventi.json.
Per aggiungere un evento: aggiungi una voce al JSON (data AAAA-MM-GG, titolo, luogo, indirizzo,
citta, testo, foto[] con src/alt/width/height; per ogni foto metti in assets/eventi/ anche la
versione piccola NOME-640.webp) e lancia: python3 tools/genera_eventi.py
Gli eventi sono ordinati dal più recente."""
import json, html, re, pathlib, datetime
R = pathlib.Path(__file__).resolve().parent.parent
SITO = "https://ilmondodibabypepita.it/"
MESI = "gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()
GIORNI = "lunedì martedì mercoledì giovedì venerdì sabato domenica".split()
ev = sorted(json.loads((R/"dati/eventi.json").read_text()), key=lambda x: x["data"], reverse=True)
e = lambda s: html.escape(s, quote=False)
def data_it(d):
    g = datetime.date.fromisoformat(d); return f"{GIORNI[g.weekday()]} {g.day} {MESI[g.month-1]} {g.year}"
def foto(f):
    p = f["src"].rsplit(".", 1)[0] + "-640.webp"
    sm = round(f["width"]*640/max(f["width"], f["height"]))
    return (f'          <li><figure><img src="{f["src"]}" srcset="{p} {sm}w, {f["src"]} {f["width"]}w" '
            f'sizes="(max-width: 639px) 45vw, 180px" alt="{html.escape(f["alt"])}" width="{f["width"]}" '
            f'height="{f["height"]}" loading="lazy" decoding="async"></figure></li>')
def scheda(x):
    par = "\n".join(f"          <p>{e(p).replace(chr(10), '<br>')}</p>" for p in x["testo"].split("\n\n"))
    luogo = ", ".join(e(v) for v in (x["luogo"], x["indirizzo"], x["citta"]) if v)
    return f'''      <li class="evento" id="{x["id"]}">
        <article aria-labelledby="titolo-{x["id"]}">
          <p class="evento-data"><time datetime="{x["data"]}">{data_it(x["data"])}</time></p>
          <h3 id="titolo-{x["id"]}">{e(x["titolo"])}</h3>
          <p class="evento-luogo">{luogo}</p>
{par}
          <ul class="evento-foto" aria-label="Foto dell'evento">
{chr(10).join(foto(f) for f in x["foto"])}
          </ul>
        </article>
      </li>'''
lista = '    <ul class="lista-eventi">\n' + "\n".join(scheda(x) for x in ev) + "\n    </ul>"
ld = {"@context": "https://schema.org", "@graph": [{"@type": "Event", "@id": SITO+"#"+x["id"], "name": x["titolo"],
      "startDate": x["data"], "eventStatus": "https://schema.org/EventScheduled",
      "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
      "location": {"@type": "Place", "name": x["luogo"], "address": {"@type": "PostalAddress",
        **({"streetAddress": x["indirizzo"]} if x["indirizzo"] else {}), "addressLocality": x["citta"], "addressCountry": "IT"}},
      "image": [SITO+f["src"] for f in x["foto"]], "description": x["testo"].split("\n")[0],
      "performer": {"@id": SITO+"#manilla"}} for x in ev]}
p = R/"index.html"; t = p.read_text()
t = re.sub(r"(<!-- EVENTI -->).*?(<!-- /EVENTI -->)", lambda m: m.group(1)+"\n"+lista+"\n    "+m.group(2), t, flags=re.S)
t = re.sub(r"(<!-- EVENTI-JSONLD -->).*?(<!-- /EVENTI-JSONLD -->)", lambda m: m.group(1)+'\n<script type="application/ld+json">\n'
           + json.dumps(ld, ensure_ascii=False, indent=1)+"\n</script>\n"+m.group(2), t, flags=re.S)
p.write_text(t); print("ok,", len(ev), "eventi")

#!/usr/bin/env python3
"""Genera le pagine del blog dagli articoli Markdown in _articoli/.
Uso: python3 tools/genera_blog.py   (dalla cartella principale del sito)
- _articoli/AAAA-MM-GG-slug.md  -> blog/slug.html
- aggiorna blog/indice.json, blog.html e sitemap.xml
- immagini: converte in webp (max 1000 px, senza EXIF) in blog/img/
- testo: solo HTML semplice, niente script/iframe; YouTube diventa un link."""
import os,re,json,html,hashlib,glob,sys,datetime
import yaml,markdown
from bs4 import BeautifulSoup
from PIL import Image,ImageOps
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
B="https://manillacastaldo.it/"
MESI="gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre novembre dicembre".split()
ALLOWED={"p","br","strong","b","em","i","u","a","h2","h3","h4","ul","ol","li","blockquote","img","figure","figcaption"}
def dit(d): return f"{int(d[8:10])} {MESI[int(d[5:7])-1]} {d[:4]}"
def slugify(s):
  s=s.lower()
  for a,b in (("àáâä","a"),("èéêë","e"),("ìíîï","i"),("òóôö","o"),("ùúûü","u")): s=re.sub(f"[{a}]",b,s)
  return re.sub(r"[^a-z0-9]+","-",s).strip("-")[:80] or "articolo"
def css_ver():
  m=re.search(r'style\.css\?v=(\d+)',open("index.html").read()); return m.group(1) if m else "1"
def immagine(src):
  """Converte un'immagine caricata dal pannello in webp ottimizzato. Ritorna (percorso relativo a blog/, w, h) o None."""
  p=src.lstrip("/")
  if src.startswith("http") or not os.path.exists(p): return None
  im=Image.open(p)
  if getattr(im,"is_animated",False): im.seek(0)
  im=ImageOps.exif_transpose(im).convert("RGB"); im.thumbnail((1000,1400))
  im=Image.frombytes("RGB",im.size,im.tobytes())   # niente EXIF/GPS
  n=hashlib.sha1(open(p,"rb").read()).hexdigest()[:14]
  out=f"blog/img/{n}.webp"
  if not os.path.exists(out): im.save(out,quality=76,method=4)
  return (f"img/{n}.webp",im.width,im.height)
def pulisci(md_text,titolo):
  h=markdown.markdown(md_text,extensions=["extra","sane_lists"])
  soup=BeautifulSoup(h,"html.parser")
  for t in soup(["script","style","noscript","object","embed","form","input","button","iframe","svg","video","audio"]): t.decompose()
  for im in soup.find_all("img"):
    r=immagine(im.get("src",""))
    if not r: im.decompose(); continue
    alt=(im.get("alt") or "").strip() or f"Immagine dall'articolo «{titolo}»"
    im.replace_with(soup.new_tag("img",src=r[0],alt=alt,width=str(r[1]),height=str(r[2]),loading="lazy",decoding="async"))
  for t in list(soup.find_all(True)):
    if t.name=="h1": t.name="h2"
    if t.name not in ALLOWED: t.unwrap(); continue
    keep={}
    if t.name=="a":
      href=t.get("href","").strip()
      if not href or href.lower().startswith(("javascript","data:","vbscript")): t.unwrap(); continue
      m=re.match(r"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)",href)
      keep["href"]=href
      if href.startswith("http") and "manillacastaldo.it" not in href and "ilmondodibabypepita.it" not in href:
        keep["target"]="_blank"; keep["rel"]="sponsored nofollow noopener" if re.search(r"amazon\.|amzn\.to",href) else "nofollow noopener"
    elif t.name=="img": keep={k:t[k] for k in ("src","alt","width","height","loading","decoding")}
    t.attrs=keep
  # link YouTube incollati da soli in un paragrafo
  for p in soup.find_all("p"):
    tx=p.get_text(strip=True)
    m=re.fullmatch(r"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)\S*",tx)
    if m and not p.find("a"):
      p.clear(); a=soup.new_tag("a",href=f"https://www.youtube.com/watch?v={m.group(1)}",target="_blank",rel="nofollow noopener"); a.string="Guarda il video su YouTube"; p.append(a)
  return str(soup),soup.get_text(" ",strip=True)
TESTA='''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{p}fonts/fonts.css">
<link rel="icon" href="{p}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{p}favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="{p}favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="{p}apple-touch-icon.png">
<link rel="stylesheet" href="{p}style.css?v={v}">
<link rel="stylesheet" href="{p}consenso/consenso-cookie.css">
<script src="{p}consenso/consenso-cookie.js" data-ga-id="G-HYYZ6MDRPR" data-informativa="{p}cookie.html" data-nome-sito="Il Mondo di Baby Pepita"></script>
'''
def pagina(prefix,title,desc,path,ogimg,ogtype,ld,body):
  q=lambda x:html.escape(x,quote=True)
  meta=f'''<title>{q(title)}</title>
<meta name="description" content="{q(desc)}">
<link rel="canonical" href="{B}{path}">
<meta property="og:type" content="{ogtype}">
<meta property="og:locale" content="it_IT">
<meta property="og:site_name" content="Il Mondo di Baby Pepita">
<meta property="og:title" content="{q(title)}">
<meta property="og:description" content="{q(desc)}">
<meta property="og:url" content="{B}{path}">
<meta property="og:image" content="{ogimg}">
<script type="application/ld+json">
{json.dumps(ld,ensure_ascii=False,indent=1)}
</script>
'''
  footer=f'<footer>© 2026 Il Mondo di Baby Pepita · manillacastaldo.it · fatto con ♥ per Manilla<br><a class="piede-link" href="{prefix}cookie.html">Cookie policy</a> · <a class="piede-link" href="#preferenze-cookie" data-preferenze-cookie>Preferenze cookie</a></footer>'
  return TESTA.format(p=prefix,v=css_ver())+meta+'</head>\n<body class="pagina pagina-blog">\n<header class="testata"><a href="'+(prefix or "./")+'">Il Mondo di <span>Baby Pepita</span></a></header>\n<main>\n'+body+'\n</main>\n'+footer+'\n</body>\n</html>\n'
PERSON={"@type":"Person","@id":B+"#manilla","name":"Manilla","url":B}
def leggi_md(f):
  t=open(f,encoding="utf-8").read()
  m=re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$",t,re.S)
  if not m: raise ValueError(f"{f}: manca l'intestazione --- titolo/data ---")
  fm=yaml.safe_load(m.group(1)) or {}; return fm,m.group(2)
def main():
  indice={a["slug"]:a for a in json.load(open("blog/indice.json"))}
  errori=[]
  for f in sorted(x for x in glob.glob("_articoli/*.md") if not x.endswith("LEGGIMI.md")):
    try: fm,testo=leggi_md(f)
    except Exception as e: errori.append(str(e)); continue
    if fm.get("bozza"): continue
    titolo=str(fm.get("titolo") or "").strip()
    if not titolo: errori.append(f"{f}: manca il titolo"); continue
    dataora=str(fm.get("data") or "").replace("T"," ")[:19]
    data=dataora[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",data): errori.append(f"{f}: data non valida"); continue
    if len(dataora)<19: dataora=data+" 12:00:00"
    slug=slugify(str(fm.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-","",os.path.basename(f)[:-3]) or titolo))
    body,text=pulisci(testo,titolo)
    cop=immagine(str(fm["copertina"])) if fm.get("copertina") else None
    cats=[str(c) for c in (fm.get("categorie") or [])]
    desc=re.sub(r"\s+"," ",str(fm.get("descrizione") or "").strip() or text)
    if len(desc)>155: desc=desc[:152].rsplit(" ",1)[0]+"…"
    if len(desc)<20: desc=f"«{titolo}», un articolo di Manilla sul blog Il Mondo di Baby Pepita."
    ld={"@context":"https://schema.org","@type":"BlogPosting","headline":titolo[:110],"datePublished":data,"dateModified":datetime.date.today().isoformat(),"author":PERSON,"publisher":{"@type":"Organization","name":"Il Mondo di Baby Pepita","url":B},"mainEntityOfPage":B+f"blog/{slug}.html","url":B+f"blog/{slug}.html","inLanguage":"it","description":desc}
    if cop: ld["image"]=B+"blog/"+cop[0]
    if cats: ld["articleSection"]=cats
    fe=f'<figure class="articolo-copertina"><img src="{cop[0]}" alt="{html.escape(str(fm.get("alt_copertina") or "Immagine di copertina dell’articolo «"+titolo+"»"))}" width="{cop[1]}" height="{cop[2]}" decoding="async"></figure>' if cop else ""
    cl=" · ".join(html.escape(c) for c in cats)
    art=f'''<article class="articolo">
  <p class="articolo-meta"><a href="../blog.html">Blog</a> · <time datetime="{data}">{dit(data)}</time>{(" · "+cl) if cl else ""}</p>
  <h1 class="articolo-titolo">{html.escape(titolo)}</h1>
  <div class="fregio" aria-hidden="true">✦ ❀ ✦</div>
  {fe}
  <div class="articolo-testo">
{body}
  </div>
  <p class="nota"><a class="btn-opere" href="../blog.html">Tutti gli articoli</a></p>
</article>'''
    open(f"blog/{slug}.html","w").write(pagina("../",f"{titolo} · Blog di Manilla",desc,f"blog/{slug}.html",B+"blog/"+cop[0] if cop else B+"assets/og-manilla.jpg","article",ld,art))
    imgs=re.findall(r'src="(img/[^"]+)" alt="[^"]*" width="(\d+)" height="(\d+)"',body)
    copl=list(cop) if cop else ([imgs[0][0],int(imgs[0][1]),int(imgs[0][2])] if imgs else None)
    indice[slug]={"slug":slug,"titolo":titolo,"data":dataora,"copertina":copl}
    print("ok:",f,"-> blog/"+slug+".html")
  arts=sorted(indice.values(),key=lambda a:a["data"],reverse=True)
  json.dump(sorted(arts,key=lambda a:a["data"]),open("blog/indice.json","w"),ensure_ascii=False,indent=0)
  anni={}
  for a in arts: anni.setdefault(a["data"][:4],[]).append(a)
  def card(a):
    c=a["copertina"]
    im=f'<img src="blog/{c[0]}" alt="" width="{c[1]}" height="{c[2]}" loading="lazy" decoding="async">' if c else '<span class="segnaposto" aria-hidden="true">❀</span>'
    return f'      <li><a class="post" href="blog/{a["slug"]}.html"><span class="post-img">{im}</span><span class="post-testo"><time datetime="{a["data"][:10]}">{dit(a["data"])}</time><span class="post-titolo">{html.escape(a["titolo"])}</span></span></a></li>'
  primo=min(anni)
  body=f'''<section class="premi-intro">
  <h1 class="titolo-pagina">Il blog di Manilla</h1>
  <div class="fregio" aria-hidden="true">✦ ❀ ✦</div>
  <p class="premi-sottotitolo">Pensieri, racconti e recensioni, dal {primo} a oggi</p>
</section>
<nav class="anni-indice" aria-label="Vai all'anno">'''+" ".join(f'<a href="#anno-{y}">{y}</a>' for y in anni)+'</nav>\n'+"\n".join(f'''<section class="blog-anno" id="anno-{y}" aria-labelledby="t-{y}">
  <h2 class="anno-titolo" id="t-{y}">{y}</h2>
  <ul class="post-lista">
{chr(10).join(card(a) for a in L)}
  </ul>
</section>''' for y,L in anni.items())+'\n<p class="nota"><a class="btn-opere" href="./">Torna alla home</a></p>'
  ld={"@context":"https://schema.org","@type":"Blog","name":"Il blog di Manilla","url":B+"blog.html","inLanguage":"it","author":PERSON,"blogPost":[{"@type":"BlogPosting","headline":a["titolo"][:110],"datePublished":a["data"][:10],"url":B+f"blog/{a['slug']}.html"} for a in arts[:20]]}
  open("blog.html","w").write(pagina("","Il blog di Manilla · Il Mondo di Baby Pepita",f"Il blog di Manilla: {len(arts)} articoli tra pensieri, racconti, recensioni e riflessioni, dal {primo} al {max(anni)}.","blog.html",B+"assets/og-manilla.jpg","website",ld,body))
  sm=open("sitemap.xml").read()
  sm=re.sub(r'\s*<url><loc>https://manillacastaldo\.it/blog/[^<]*</loc>.*?</url>','',sm)
  add="".join(f'\n  <url><loc>{B}blog/{a["slug"]}.html</loc><lastmod>{a["data"][:10]}</lastmod></url>' for a in sorted(arts,key=lambda a:a["data"]))
  sm=sm.replace("\n</urlset>",add+"\n</urlset>")
  open("sitemap.xml","w").write(sm)
  print("blog.html:",len(arts),"articoli; sitemap:",sm.count("<url>"),"URL")
  if errori:
    print("ERRORI:",*errori,sep="\n- "); sys.exit(1)
if __name__=="__main__": main()

# Pannello di Manilla (Decap CMS) – come funziona

## Per Manilla
1. Apre https://ilmondodibabypepita.it/admin/ e preme «Accedi con GitHub» (account GitHub suo, gratuito).
2. «Nuovo Articolo»: titolo, data, categorie, foto di copertina, descrizione della foto, testo.
3. «Salva»: resta una bozza (nessuno la vede sul sito).
4. Quando è pronta: stato «Pronto» → «Pubblica». In 1–3 minuti l'articolo compare nel blog.

## Cosa succede dietro
- Il pannello salva `_articoli/AAAA-MM-GG-titolo.md` e le foto in `immagini-caricate/` nel repo.
- La GitHub Action `.github/workflows/blog.yml` esegue `tools/genera_blog.py`: crea `blog/<slug>.html`
  con lo stesso stile, foto in webp senza EXIF, alt, SEO, JSON-LD, GA4 con consenso; aggiorna `blog.html`,
  `blog/indice.json` e `sitemap.xml`. Script, iframe e codice vengono tolti dal testo.

## Da attivare (non fatto)
1. Account GitHub per Manilla + invito come collaboratrice del repo (permesso Write).
2. Ponte OAuth per il login GitHub: es. Cloudflare Worker gratuito (sveltia-cms-auth o decap-proxy),
   OAuth App GitHub con callback sul Worker, poi `base_url` in `admin/config.yml`.
3. Verificare che il commit dell'Action faccia ripartire GitHub Pages; se no, Pages → «GitHub Actions».

## Prova in locale
    npx decap-server &           # nella cartella del sito
    python3 -m http.server 8080  # poi apri http://localhost:8080/admin/
    python3 tools/genera_blog.py

## Tornare indietro
Ogni salvataggio è un commit: `git revert <commit>` e push normale. Il pannello non può cancellare articoli (delete: false).

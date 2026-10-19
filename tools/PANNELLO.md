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

## Permessi scelti (minimi possibili con Decap + backend github)
- **Manilla86: ruolo `write`** (non maintain/admin): Decap scrive via API GitHub col token di chi entra,
  quindi serve scrittura. Non può cambiare impostazioni, segreti, collaboratori né le regole.
- **`publish_mode: editorial_workflow`**: ogni bozza va su un ramo `cms/...` con una PR; «Pubblica» = merge.
- **Ruleset «Proteggi main»**: vieta force push e cancellazione del ramo main (per tutti, Titolare incluso).
  Non obblighiamo la PR con revisione su main, altrimenti la GitHub Action che rigenera il blog non potrebbe pushare.
- **Workflow `controllo-percorsi.yml`**: sulle PR dei rami `cms/**` e sui push di Manilla86 fallisce se
  sono toccati file fuori da `_articoli/` e `immagini-caricate/` (segnale rosso + email al Titolare).
- **CODEOWNERS**: tutto al Titolare; `_articoli/` e `immagini-caricate/` anche a Manilla.
- **Pannello ristretto**: in `admin/config.yml` c'è solo la collezione «Articoli» (niente home/Premi/Opere), `delete: false`.
- Limite onesto: con `write` Manilla *tecnicamente* potrebbe modificare altri file via git/API fuori dal pannello;
  il controllo lo rende visibile e ogni modifica è un commit revertibile, ma non lo impedisce.

## Checklist di attivazione
### A. Dal Titolare (Arcangelo)
- [ ] Account Cloudflare gratuito creato **da lui**, con login fatto da lui sul suo computer (email + 2FA suoi).
- [ ] Login GitHub come `castaldoarcangelo88-source` (per OAuth App e per lanciare lo script).

### B. Worker OAuth gratuito su Cloudflare
1. [ ] Cloudflare → Workers & Pages → Create → Worker da template/repo `sveltia-cms-auth` (o `decap-proxy`);
       nome es. `pannello-oauth` → URL `https://pannello-oauth.<account>.workers.dev`.
2. [ ] GitHub → Settings → Developer settings → OAuth Apps → New OAuth App:
       Homepage `https://ilmondodibabypepita.it`, Authorization callback URL `https://pannello-oauth.<account>.workers.dev/callback`.
       Genera il Client secret.
3. [ ] Worker → Settings → Variables and Secrets: `GITHUB_CLIENT_ID` e `GITHUB_CLIENT_SECRET` (tipo *Secret*);
       se il template lo prevede `ALLOWED_DOMAINS=ilmondodibabypepita.it`. Deploy.
4. [ ] Lanciare `tools/attiva-pannello.sh https://pannello-oauth.<account>.workers.dev` (chiede conferma):
       crea il ruleset su main, invita Manilla86 (write), stampa i passi finali.
5. [ ] Impostare `base_url` in `admin/config.yml`, merge di `pannello-manilla` su main, verificare che
       Pages si aggiorni dopo il commit dell'Action (se no: Pages → origine «GitHub Actions»).

### C. Cosa riceve Manilla
- [ ] Email di invito GitHub → accettare (o https://github.com/castaldoarcangelo88-source/wip-site-b/invitations).
- [ ] Link del pannello: https://ilmondodibabypepita.it/admin/ → «Accedi con GitHub».
- [ ] Prova guidata: una bozza → «Pronto» → «Pubblica» → articolo online in 1–3 minuti.

## Prova in locale
    npx decap-server &           # nella cartella del sito
    python3 -m http.server 8080  # poi apri http://localhost:8080/admin/
    python3 tools/genera_blog.py

## Tornare indietro
Ogni salvataggio è un commit: `git revert <commit>` e push normale. Il pannello non può cancellare articoli (delete: false).

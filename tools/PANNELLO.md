# Pannello di Manilla (Decap CMS) – come funziona

## Per Manilla
1. Apre https://manillacastaldo.it/admin/ e preme «Accedi con GitHub» (account GitHub suo, gratuito).
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

## Stato finale (19/10/2026, ore 10:52 ora di Roma) – PANNELLO ATTIVO
- Worker OAuth: https://decap-oauth-babypepita.castaldoarcangelo88.workers.dev (segreti GITHUB_CLIENT_ID /
  GITHUB_CLIENT_SECRET impostati; `/auth` → 302 verso GitHub, client_id `Ov23lirSwyiTG8ZMs6i9`, scope `public_repo`).
  Origini ammesse: https://manillacastaldo.it e https://www.manillacastaldo.it (durante la migrazione anche https://ilmondodibabypepita.it e https://www.ilmondodibabypepita.it).
- OAuth App GitHub «Pannello blog Baby Pepita», callback `…workers.dev/callback`. «Expire user access tokens» attivo:
  il token dura 8 ore e Decap non lo rinnova, quindi dopo 8 ore Manilla deve rifare «Accedi con GitHub».
- `admin/config.yml`: backend github, repo `castaldoarcangelo88-source/wip-site-b`, branch `main`,
  `base_url` = Worker, `auth_endpoint: auth`, `publish_mode: editorial_workflow`.
- `admin/index.html`: `noindex, nofollow`; Decap 3.3.3 da unpkg con SRI
  `sha384-Ch3bpZcxxjHMuIde+QMTyDdxGqjtafFkpoGgvLjf50nHhptNH7bZyPTyKSkOvEo+`. /admin non è in sitemap.xml.
  Per aggiornare Decap: cambiare versione **e** ricalcolare l'hash
  (`curl -sL URL | openssl dgst -sha384 -binary | base64`), altrimenti il pannello non si carica.
- Merge su main: commit `72bc49a` (merge di `pannello-manilla` @ `272aa94`). Il ramo `poesia-premio` NON è incluso.
- Ruleset «Proteggi main» (id 25389252) attivo: niente force push né cancellazione di main.
- Invito a Manilla86 con permesso `write` (invito id 338471430, inviato il 19/10/2026; scade dopo 7 giorni se non accettato).
- Verificato: https://manillacastaldo.it/admin/ → 200, Decap si carica e «Accedi con GitHub» apre il login GitHub.

### Tornare indietro (pannello intero)
1. `git revert -m 1 72bc49a` e push normale su main (toglie /admin, Action e strumenti).
2. Togliere l'invito/accesso: `gh api -X DELETE repos/castaldoarcangelo88-source/wip-site-b/invitations/338471430`
   (se già accettato: `gh api -X DELETE repos/castaldoarcangelo88-source/wip-site-b/collaborators/Manilla86`).
3. GitHub → Settings → Developer settings → OAuth Apps → «Pannello blog Baby Pepita» → «Revoke all user tokens»
   (ed eventualmente elimina l'app); su Cloudflare si può eliminare il Worker `decap-oauth-babypepita`.

## Checklist di attivazione (storico)
### A. Dal Titolare (Arcangelo)
- [ ] Account Cloudflare gratuito creato **da lui**, con login fatto da lui sul suo computer (email + 2FA suoi).
- [ ] Login GitHub come `castaldoarcangelo88-source` (per OAuth App e per lanciare lo script).

### B. Worker OAuth gratuito su Cloudflare
1. [ ] Cloudflare → Workers & Pages → Create → Worker da template/repo `sveltia-cms-auth` (o `decap-proxy`);
       nome es. `pannello-oauth` → URL `https://pannello-oauth.<account>.workers.dev`.
2. [ ] GitHub → Settings → Developer settings → OAuth Apps → New OAuth App:
       Homepage `https://manillacastaldo.it`, Authorization callback URL `https://pannello-oauth.<account>.workers.dev/callback`.
       Genera il Client secret.
3. [ ] Worker → Settings → Variables and Secrets: `GITHUB_CLIENT_ID` e `GITHUB_CLIENT_SECRET` (tipo *Secret*);
       se il template lo prevede `ALLOWED_DOMAINS=manillacastaldo.it,ilmondodibabypepita.it`. Deploy.
4. [ ] Lanciare `tools/attiva-pannello.sh https://pannello-oauth.<account>.workers.dev` (chiede conferma):
       crea il ruleset su main, invita Manilla86 (write), stampa i passi finali.
5. [ ] Impostare `base_url` in `admin/config.yml`, merge di `pannello-manilla` su main, verificare che
       Pages si aggiorni dopo il commit dell'Action (se no: Pages → origine «GitHub Actions»).

### C. Cosa riceve Manilla
- [ ] Email di invito GitHub → accettare (o https://github.com/castaldoarcangelo88-source/wip-site-b/invitations).
- [ ] Link del pannello: https://manillacastaldo.it/admin/ → «Accedi con GitHub».
- [ ] Prova guidata: una bozza → «Pronto» → «Pubblica» → articolo online in 1–3 minuti.

## Prova in locale
    npx decap-server &           # nella cartella del sito
    python3 -m http.server 8080  # poi apri http://localhost:8080/admin/
    python3 tools/genera_blog.py

## Tornare indietro
Ogni salvataggio è un commit: `git revert <commit>` e push normale. Il pannello non può cancellare articoli (delete: false).

#!/usr/bin/env bash
# Attivazione del pannello di Manilla. NON lanciare finché il Worker OAuth non è pronto.
# Uso: tools/attiva-pannello.sh https://pannello-oauth.NOME.workers.dev
set -euo pipefail
REPO="castaldoarcangelo88-source/wip-site-b"
UTENTE="Manilla86"
URL="${1:-}"
[[ "$URL" =~ ^https://[A-Za-z0-9.-]+(/.*)?$ ]] || { echo "Uso: $0 https://<worker-oauth>"; exit 1; }
URL="${URL%/}"
command -v gh >/dev/null || { echo "Serve gh (GitHub CLI) autenticato come Titolare"; exit 1; }
gh api "users/$UTENTE" --jq .login >/dev/null || { echo "Utente $UTENTE non trovato"; exit 1; }
echo "Repo: $REPO | Collaboratrice: $UTENTE (write) | Worker OAuth: $URL"
echo "Farò: 1) ruleset su main (no force push, no cancellazione)  2) invito $UTENTE con permesso write"
read -r -p "Confermi? Scrivi SI: " R; [ "$R" = "SI" ] || { echo "Annullato."; exit 1; }

echo "== 1) Protezione del ramo main =="
if gh api "repos/$REPO/rulesets" --jq '.[].name' | grep -qx "Proteggi main"; then
  echo "Ruleset già presente, salto."
else
  gh api -X POST "repos/$REPO/rulesets" --input - <<JSON
{"name":"Proteggi main","target":"branch","enforcement":"active",
 "conditions":{"ref_name":{"include":["~DEFAULT_BRANCH"],"exclude":[]}},
 "rules":[{"type":"deletion"},{"type":"non_fast_forward"}]}
JSON
fi

echo "== 2) Invito $UTENTE (write) =="
gh api -X PUT "repos/$REPO/collaborators/$UTENTE" -f permission=push >/dev/null
echo "Invito inviato (o permesso aggiornato)."

echo "== 3) Passi rimanenti =="
cat <<TXT
- In admin/config.yml togli il # da base_url e metti: base_url: $URL
  poi commit + push su main (o merge del ramo pannello-manilla).
- Controlla che la OAuth App GitHub abbia callback: $URL/callback
- Sul Worker devono esserci i segreti GITHUB_CLIENT_ID e GITHUB_CLIENT_SECRET.
- Manilla: accetta l'invito su https://github.com/$REPO/invitations, poi apre
  https://ilmondodibabypepita.it/admin/ → «Accedi con GitHub».
- Prova: una bozza, «Pubblica», verifica il blog dopo 1–3 minuti.
TXT

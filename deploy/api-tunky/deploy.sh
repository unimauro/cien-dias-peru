#!/bin/bash
# Despliega el asistente de «100 días bajo la lupa» (cien.js) en api.tunky.net (VPS /opt/api-tunky).
# No toca /pais ni /agenda. Respaldo de server.js y cien.js, chequeo de sintaxis ANTES de reconstruir,
# rollback automático si falla el chequeo, y prueba al final. Nunca usa `down` ni `-v`.
# Requisito previo: publicar data/chat.json en GitHub Pages (git push) — el backend lo lee de ahí.
# Uso (desde la raíz del repo):  bash deploy/api-tunky/deploy.sh
set -euo pipefail
VPS=root@217.15.168.100
DIR="$(cd "$(dirname "$0")" && pwd)"
node -c "$DIR/cien.js" 2>/dev/null || echo "(sin node local: se valida en el VPS)"
echo "--- data/chat.json publicado ---"
curl -s -o /dev/null -w "%{http_code}\n" https://unimauro.github.io/cien-dias-peru/data/chat.json
scp -q "$DIR/cien.js" "$DIR/patch.py" "$VPS:/tmp/"
ssh "$VPS" 'set -e; cd /opt/api-tunky
  TS=$(date +%s)
  cp src/server.js "src/server.js.bak.cien.$TS"
  [ -f src/cien.js ] && cp src/cien.js "src/cien.js.bak.$TS" || true
  cp /tmp/cien.js src/cien.js
  python3 /tmp/patch.py
  if ! docker run --rm -v /opt/api-tunky/src:/s:ro node:20-alpine sh -c "node -c /s/server.js && node -c /s/cien.js"; then
    echo "ERROR de sintaxis: restaurando respaldo"; cp "src/server.js.bak.cien.$TS" src/server.js
    [ -f "src/cien.js.bak.$TS" ] && cp "src/cien.js.bak.$TS" src/cien.js || rm -f src/cien.js
    exit 1
  fi
  docker compose up -d --build api-tunky
  sleep 6; docker logs --tail 8 api-tunky'
echo "--- prueba ---"
curl -s https://api.tunky.net/health; echo
curl -s -X POST -H "Origin: https://unimauro.github.io" -H "Content-Type: application/json" \
  -d '{"q":"¿Quién tuvo más cambios de ministros, Castillo o Keiko?"}' https://api.tunky.net/cien/chat | head -c 800; echo
echo "--- origen no permitido (debe dar 403) ---"
curl -s -o /dev/null -w "%{http_code}\n" -X POST -H "Origin: https://evil.example" -H "Content-Type: application/json" -d '{"q":"hola"}' https://api.tunky.net/cien/chat

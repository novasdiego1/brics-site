#!/usr/bin/env bash
# deploy.sh — Corre el pipeline completo: fetch datos -> genera gráficos -> despliega a Cloudflare Pages.
# Pensado para correr por cron. Asume que ya hiciste el setup de una sola vez (ver README).

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Activa el venv si existe (ajusta la ruta si tu venv está en otro lado)
if [ -f "../venv/bin/activate" ]; then
  source ../venv/bin/activate
fi

echo "[$(date -Iseconds)] Descargando datos..."
python3 fetch_data.py --days 730 --out ../data/market_data.csv

echo "[$(date -Iseconds)] Generando gráficos..."
python3 build_charts.py --csv ../data/market_data.csv --outdir ../site/img

echo "[$(date -Iseconds)] Desplegando a Cloudflare Pages..."
cd ../site
npx wrangler pages deploy . --project-name=radar-desdolarizacion --commit-dirty=true

echo "[$(date -Iseconds)] Listo."

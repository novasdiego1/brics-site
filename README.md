# Radar Desdolarización — MVP técnico

## Qué es esto
Prototipo funcional (probado con datos sintéticos, ver nota abajo) del tracker BRICS/desdolarización que discutimos: BTC vs Oro vs DXY indexados, correlación móvil, y una línea de tiempo de eventos verificados.

## Estructura
```
brics-tracker/
├── scripts/
│   ├── fetch_data.py      # descarga BTC-USD, GC=F (oro), DX-Y.NYB (dólar) vía yfinance
│   └── build_charts.py    # genera los 2 PNG a partir del CSV
├── data/
│   └── market_data.csv    # se genera con fetch_data.py
├── site/
│   ├── index.html         # página estática que muestra los gráficos
│   └── img/                # PNGs generados por build_charts.py
└── README.md
```

## IMPORTANTE — nota sobre esta prueba
Este sandbox no tiene salida a internet libre (solo repositorios de paquetes), así que no pude probar `fetch_data.py` contra Yahoo Finance real desde aquí. Lo que sí verifiqué es la lógica completa de `build_charts.py` con datos sintéticos — los gráficos que viste en el chat son de esa prueba, no son datos reales de mercado.

**Necesitas correr `fetch_data.py` en tu propia máquina/servidor** (con internet normal) para bajar los datos reales. Ahí sí debería funcionar sin cambios — yfinance es una librería madura y muy usada, pero como con cualquier scraper de Yahoo Finance puede eventualmente cambiar de formato; si falla, es la primera línea de debug.

## Cómo correrlo
```bash
pip install yfinance pandas matplotlib

cd scripts
python3 fetch_data.py --days 730 --out ../data/market_data.csv
python3 build_charts.py --csv ../data/market_data.csv --outdir ../site/img
```

Después abre `site/index.html` en el navegador.

## Automatización y hosting: GitHub Actions + GitHub Pages

Esta es la vía recomendada (más simple que un cron local + Cloudflare Pages/Wrangler — no depende de que tu máquina esté encendida, todo corre en la nube de GitHub gratis).

`deploy.sh` (Wrangler/Cloudflare Pages) queda en el repo como alternativa por si algún día prefieres tener el sitio en tu propia infraestructura, pero no es necesario — no lo uses junto con GitHub Actions, son dos caminos distintos al mismo resultado.

### Setup (una sola vez)

1. Crea un repo en GitHub (puede ser privado o público, no importa) y sube esta carpeta:
   ```bash
   cd brics-tracker
   git init
   git add .
   git commit -m "Radar Desdolarización — setup inicial"
   git branch -M main
   git remote add origin git@github.com:<tu-usuario>/brics-tracker.git
   git push -u origin main
   ```

2. En GitHub: **Settings → Pages → Build and deployment → Source: "GitHub Actions"**. (No selecciones una rama — el workflow ya incluido en `.github/workflows/update.yml` hace el deploy directo.)

3. Dominio propio: el archivo `site/CNAME` ya trae `radar.criptomix.com`. En GoDaddy/Namecheap (donde esté el DNS de criptomix.com) agrega:
   - **Tipo:** CNAME
   - **Host:** `radar`
   - **Apunta a:** `<tu-usuario>.github.io`

   GitHub emite el certificado SSL solo, una vez que detecta el CNAME (puede tardar unos minutos a un par de horas).

4. El workflow corre solo todos los días a las 6am hora Honduras (`cron: "0 12 * * *"` en UTC) y también lo puedes disparar manualmente desde la pestaña **Actions → Actualizar y publicar Radar Desdolarización → Run workflow**.

### Nota sobre "promoción"
GitHub Pages y Cloudflare son hosting/CDN, no herramientas de SEO — no "promueven" el sitio por sí solos. El tráfico real depende del contenido (la pieza de la moneda BRICS, etc.) y de que Google indexe el sitio. Vale la pena, cuando esté publicado, darlo de alta en Google Search Console — eso sí ayuda a que aparezca en resultados de búsqueda más rápido.

## Lo que falta para producción (no lo armé todavía, a propósito)
- Curación manual de la línea de tiempo de eventos (10-15 min/semana, como hablamos).
- La pieza de contenido "¿existe una moneda BRICS real?" — la de mayor prioridad por el hallazgo de +1,250% en búsquedas de "brics currency" y los tokens falsos que están circulando.
- Dominio/hosting real y diseño visual más trabajado (esto es intencionalmente minimalista, es un esqueleto funcional).
- Reservas de oro de bancos centrales BRICS (World Gold Council) — dato trimestral, se agrega aparte porque no es diario como BTC/oro/DXY.

#!/usr/bin/env python3
"""
fetch_news.py — Descarga titulares recientes sobre BRICS desde Google News RSS
(sin API key) y los guarda como JSON para que el sitio los muestre.

IMPORTANTE: estos titulares NO están verificados uno por uno — es una lista
automática de lo que está circulando, no un fact-check. El sitio los muestra
separados de la sección de "hechos verificados" para no mezclar ambas cosas.

Uso:
    python3 fetch_news.py --query "BRICS" --lang es-419 --out ../site/data/news.json --limit 10
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote

USER_AGENT = "Mozilla/5.0 (compatible; radar-desdolarizacion/1.0)"


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_feed(query: str, lang: str) -> bytes:
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl={lang}&gl=US&ceid=US:{lang}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def parse_items(xml_bytes: bytes, limit: int) -> list:
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall(".//item")[: limit * 2]:  # margen por si hay que filtrar
        title = strip_html(item.findtext("title") or "")
        link = (item.findtext("link") or "").strip()
        pub_date_raw = item.findtext("pubDate") or ""
        source_el = item.find("source")
        source = source_el.text.strip() if source_el is not None and source_el.text else ""

        try:
            pub_dt = parsedate_to_datetime(pub_date_raw)
            if pub_dt.tzinfo is None:
                pub_dt = pub_dt.replace(tzinfo=timezone.utc)
            pub_iso = pub_dt.astimezone(timezone.utc).isoformat()
        except Exception:
            pub_iso = None

        if not title or not link:
            continue

        items.append({
            "title": title,
            "link": link,
            "source": source,
            "published": pub_iso,
        })

    # Ordena por fecha descendente cuando hay fecha; si no, deja el orden del feed.
    items.sort(key=lambda x: x["published"] or "", reverse=True)
    return items[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="BRICS")
    ap.add_argument("--lang", default="es-419")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--out", default="../site/data/news.json")
    args = ap.parse_args()

    try:
        raw = fetch_feed(args.query, args.lang)
        items = parse_items(raw, args.limit)
    except Exception as e:
        print(f"AVISO: no se pudo descargar/parsear el feed de noticias: {e}", file=sys.stderr)
        items = []

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query": args.query,
        "note": "Titulares obtenidos automáticamente de Google News. NO están verificados individualmente — ver sección 'Hechos verificados' para análisis con fuente confirmada.",
        "items": items,
    }

    outdir = os.path.dirname(args.out)
    if outdir:
        os.makedirs(outdir, exist_ok=True)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Guardado: {args.out} ({len(items)} noticias)")


if __name__ == "__main__":
    main()

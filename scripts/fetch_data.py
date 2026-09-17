#!/usr/bin/env python3
"""
fetch_data.py — Descarga BTC, oro y el índice dólar (DXY) y guarda un CSV
consolidado para el tracker de desdolarización/BRICS.

Fuente: Yahoo Finance vía yfinance (gratis, sin API key).
Tickers:
  - BTC-USD     -> Bitcoin
  - GC=F        -> Futuros de oro (COMEX)
  - DX-Y.NYB    -> Índice dólar (ICE US Dollar Index)

Uso:
    python3 fetch_data.py --days 730 --out ../data/market_data.csv

Pensado para correr diario vía cron. No requiere claves ni cuentas.
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd
import yfinance as yf

TICKERS = {
    "BTC-USD": "btc_usd",
    "GC=F": "gold_usd",
    "DX-Y.NYB": "dxy",
}


def fetch(days: int) -> pd.DataFrame:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    frames = []
    for ticker, colname in TICKERS.items():
        print(f"Descargando {ticker} ({colname})...", file=sys.stderr)
        hist = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=True,
        )
        if hist.empty:
            print(f"  AVISO: sin datos para {ticker}", file=sys.stderr)
            continue
        # yfinance a veces devuelve MultiIndex de columnas — nos quedamos con Close
        close = hist["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        close.name = colname
        frames.append(close)

    if not frames:
        raise RuntimeError("No se pudo descargar ningún ticker. Revisa conexión/red.")

    df = pd.concat(frames, axis=1)
    df.index.name = "date"
    df = df.sort_index().ffill()  # rellena días sin cierre (feriados distintos por mercado)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=730, help="Días de histórico a bajar")
    ap.add_argument("--out", type=str, default="../data/market_data.csv")
    args = ap.parse_args()

    df = fetch(args.days)
    df.to_csv(args.out)
    print(f"Guardado: {args.out} ({len(df)} filas, rango {df.index.min().date()} a {df.index.max().date()})")


if __name__ == "__main__":
    main()

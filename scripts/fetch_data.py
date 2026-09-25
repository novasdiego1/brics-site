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
    # Monedas BRICS vs USD (Yahoo Finance: <MONEDA>=X es USD -> moneda,
    # o sea "cuántas unidades de esa moneda vale 1 dólar")
    "BRL=X": "usd_brl",
    "INR=X": "usd_inr",
    "CNY=X": "usd_cny",
    "ZAR=X": "usd_zar",
    # Rusia (RUB=X) se omite a propósito: el dato en Yahoo Finance es poco
    # confiable desde las sanciones de 2022 (feed intermitente/desactualizado).
}


def fetch(days: int) -> pd.DataFrame:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    frames = []
    for ticker, colname in TICKERS.items():
        print(f"Descargando {ticker} ({colname})...", file=sys.stderr)
        try:
            hist = yf.download(
                ticker,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=True,
            )
        except Exception as e:
            print(f"  AVISO: error descargando {ticker}: {e}", file=sys.stderr)
            continue
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

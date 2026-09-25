#!/usr/bin/env python3
"""
build_charts.py — Genera los 2 gráficos base del tracker a partir del CSV
producido por fetch_data.py:

  1. chart_indexed.png  — BTC vs Oro vs DXY, indexados a 100 (un solo eje,
     nunca doble eje — son series de escalas muy distintas).
  2. chart_correlation.png — correlación móvil de 30 días entre BTC y Oro,
     con relleno divergente (azul = correlación positiva, naranja = negativa).

Paleta: la paleta categórica validada del skill dataviz (references/palette.md).

Uso:
    python3 build_charts.py --csv ../data/market_data.csv --outdir ../site/img
"""

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# Paleta validada (light mode) — slots 1-4 del skill dataviz (adjacent-pairs
# safe, correcto para líneas de series de tiempo)
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
SURFACE = "#fcfcfb"
GRID = "#e4e3de"


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=9)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))


def chart_indexed(df: pd.DataFrame, outpath: str):
    base = df.iloc[0]
    idx = df.divide(base).multiply(100)

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    ax.plot(idx.index, idx["btc_usd"], color=BLUE, linewidth=2, label="Bitcoin", solid_capstyle="round")
    ax.plot(idx.index, idx["gold_usd"], color=ORANGE, linewidth=2, label="Oro", solid_capstyle="round")
    ax.plot(idx.index, idx["dxy"], color=AQUA, linewidth=2, label="Índice dólar (DXY)", solid_capstyle="round")
    ax.axhline(100, color=GRID, linewidth=1, linestyle="--", zorder=0)

    style_axes(ax)
    ax.set_title("BTC vs Oro vs DXY — indexado a 100 en el punto de partida", fontsize=13, color=TEXT_PRIMARY, loc="left", pad=14)
    ax.set_ylabel("Índice (base 100)", fontsize=10, color=TEXT_SECONDARY)
    ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=TEXT_PRIMARY)

    fig.tight_layout()
    fig.savefig(outpath, facecolor=SURFACE)
    plt.close(fig)


def chart_correlation(df: pd.DataFrame, outpath: str, window: int = 30):
    ret_btc = df["btc_usd"].pct_change()
    ret_gold = df["gold_usd"].pct_change()
    corr = ret_btc.rolling(window).corr(ret_gold)

    fig, ax = plt.subplots(figsize=(10, 4), dpi=150)
    ax.fill_between(corr.index, corr, 0, where=(corr >= 0), color=BLUE, alpha=0.25, linewidth=0)
    ax.fill_between(corr.index, corr, 0, where=(corr < 0), color=ORANGE, alpha=0.25, linewidth=0)
    ax.plot(corr.index, corr, color=TEXT_PRIMARY, linewidth=1.4)
    ax.axhline(0, color=GRID, linewidth=1)

    style_axes(ax)
    ax.set_ylim(-1, 1)
    ax.set_title(f"Correlación móvil {window}d entre retornos de BTC y Oro", fontsize=13, color=TEXT_PRIMARY, loc="left", pad=14)
    ax.set_ylabel("Correlación", fontsize=10, color=TEXT_SECONDARY)

    fig.tight_layout()
    fig.savefig(outpath, facecolor=SURFACE)
    plt.close(fig)


def chart_currencies(df: pd.DataFrame, outpath: str):
    """
    Monedas BRICS vs USD, indexado a 100. Los tickers de Yahoo Finance dan
    "cuántas unidades de la moneda vale 1 USD" — para que "sube = la moneda
    se fortalece frente al dólar" (la lectura intuitiva para esta tesis),
    invertimos la serie antes de indexar.
    """
    cols = {
        "usd_brl": ("Real brasileño", BLUE),
        "usd_inr": ("Rupia india", ORANGE),
        "usd_cny": ("Yuan chino", AQUA),
        "usd_zar": ("Rand sudafricano", YELLOW),
    }
    available = [c for c in cols if c in df.columns]
    if not available:
        print("AVISO: no hay columnas de monedas BRICS en el CSV, se omite el gráfico.")
        return

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    for col in available:
        inverted = 1 / df[col]
        idx = inverted.divide(inverted.iloc[0]).multiply(100)
        label, color = cols[col]
        ax.plot(idx.index, idx, color=color, linewidth=2, label=label, solid_capstyle="round")
    ax.axhline(100, color=GRID, linewidth=1, linestyle="--", zorder=0)

    style_axes(ax)
    ax.set_title("Monedas BRICS vs USD — indexado a 100 (sube = moneda se fortalece frente al dólar)",
                 fontsize=12, color=TEXT_PRIMARY, loc="left", pad=14)
    ax.set_ylabel("Índice (base 100)", fontsize=10, color=TEXT_SECONDARY)
    ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=TEXT_PRIMARY)

    fig.tight_layout()
    fig.savefig(outpath, facecolor=SURFACE)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, default="../data/market_data.csv")
    ap.add_argument("--outdir", type=str, default="../site/img")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    df = pd.read_csv(args.csv, index_col="date", parse_dates=True)

    chart_indexed(df, os.path.join(args.outdir, "chart_indexed.png"))
    chart_correlation(df, os.path.join(args.outdir, "chart_correlation.png"))
    chart_currencies(df, os.path.join(args.outdir, "chart_currencies.png"))

    latest_corr = df["btc_usd"].pct_change().rolling(30).corr(df["gold_usd"].pct_change()).iloc[-1]
    print(f"Listo. Correlación BTC-Oro (30d) más reciente: {latest_corr:.2f}")


if __name__ == "__main__":
    main()

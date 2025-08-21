#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_tryd_signals.py

Standalone daily signal generator for the FuzzyFajuto strategy on B3 tickers.

- Fetches last 20 daily bars via yfinance
- Computes indicators (EMAs: 3,5,10,15,20; RSI: 10) using pandas/numpy
- Scores per spec: Return vs Ibov (+1/-1), EMAs (±0.25 each), RSI (±0.25)
- Signals: BUY if score >= +1.50; SELL if score <= -1.50
- Sizing: 50,000 BRL notional per symbol; quantity = 50000 / last_close
  rounded to nearest 100 shares (board-lot)
- Exports Tryd Automate Excel file (automate.xlsx) with official columns

No external configs or repository modules required.
"""

from __future__ import annotations

import datetime as dt
from typing import Dict, List, Tuple
import os
import time

import numpy as np
import pandas as pd
import requests
from openpyxl import Workbook


IBOV: str = '^BVSP'
BRAPI_BASE_URL: str = 'https://brapi.dev/api'
BRAPI_TOKEN: str = '5c1YnnPjkXaX2PFcLYjARZ'

# Business rules
EMA_PERIODS: List[int] = [3, 5, 10, 15, 20]
RSI_PERIOD: int = 10
RSI_OVERBOUGHT: float = 65.0
RSI_OVERSOLD: float = 35.0
BUY_THRESHOLD: float = 1.50
SELL_THRESHOLD: float = -1.50
NOTIONAL_PER_SYMBOL: float = 50000.0

# Tryd Automate columns
TRYD_HEADERS: List[str] = [
    'Papel', 'Cód. Cliente', 'Cond. Compra', 'Máx. Qtd. Compra', 'Qtd. Apar. Compra',
    'Qtd. Compra', 'Preço Compra', 'Preço Venda', 'Qtd. Venda', 'Qtd. Apar. Venda',
    'Máx. Qtd. Venda', 'Cond. Venda', 'Observação'
]


def _brapi_fetch_chunk(symbols: List[str], range_param: str = '3mo', interval: str = '1d', retry_count: int = 0) -> Dict[str, dict]:
    joined = ','.join(symbols)
    url = f"{BRAPI_BASE_URL}/quote/{joined}"
    headers = {"Authorization": f"Bearer {BRAPI_TOKEN}"}
    params = {"range": range_param, "interval": interval, "fundamental": "true", "dividends": "false"}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        if resp.status_code == 429 and retry_count < 3:  # Rate limit - retry with delay
            wait_time = (retry_count + 1) * 2  # Exponential backoff
            print(f"Rate limit hit, waiting {wait_time}s before retry {retry_count + 1}/3...")
            time.sleep(wait_time)
            return _brapi_fetch_chunk(symbols, range_param, interval, retry_count + 1)
        elif resp.status_code != 200:
            print(f"brapi API error: status={resp.status_code} for symbols={joined[:50]}...")
            # Try individual symbols if chunk fails
            if len(symbols) > 1:
                print(f"Retrying symbols individually...")
                out = {}
                for sym in symbols:
                    time.sleep(0.3)  # Small delay between individual calls
                    res = _brapi_fetch_chunk([sym], range_param, interval, retry_count)
                    out.update(res)
                return out
            return {}
        payload = resp.json() or {}
        results = payload.get('results') or []
        out: Dict[str, dict] = {}
        for r in results:
            sym = r.get('symbol') or r.get('symbolName')
            if sym:
                out[sym] = r
        return out
    except Exception as e:
        print(f"brapi API exception: {e} for symbols={joined[:50]}...")
        return {}


def fetch_last_n_bars(tickers: List[str], n: int = 20) -> Dict[str, pd.DataFrame]:
    data: Dict[str, pd.DataFrame] = {}
    # Prepare list without duplicates; include IBOV
    all_syms = list(dict.fromkeys(list(tickers) + [IBOV]))

    # Reduce chunk size to avoid rate limits and add delay between calls
    chunk_size = 10  # Reduced from 50 to avoid rate limits
    merged_results: Dict[str, dict] = {}
    
    # Fetch IBOV first (most important)
    if IBOV in all_syms:
        res = _brapi_fetch_chunk([IBOV], range_param='3mo', interval='1d')
        merged_results.update(res)
        all_syms.remove(IBOV)
        time.sleep(0.5)  # Small delay to avoid rate limits
    
    # Fetch remaining symbols in chunks
    for i in range(0, len(all_syms), chunk_size):
        chunk = all_syms[i:i+chunk_size]
        res = _brapi_fetch_chunk(chunk, range_param='3mo', interval='1d')
        merged_results.update(res)
        if i + chunk_size < len(all_syms):  # Don't sleep after last chunk
            time.sleep(0.5)  # Delay between chunks to avoid rate limits

    # ^BVSP works and returns historicalDataPrice; avoid mapping to IBOV alias

    # Process all fetched results (not just all_syms since we removed IBOV from it)
    for sym, r in merged_results.items():
        if not r:
            data[sym] = pd.DataFrame()
            continue
        hist = r.get('historicalDataPrice') or []
        # Build DataFrame
        if hist:
            df = pd.DataFrame(hist)
            # Expected keys: date (unix or iso), open, high, low, close, volume
            # Normalize date
            if 'date' in df.columns:
                # brapi often returns timestamp (seconds)
                df['date'] = pd.to_datetime(df['date'], unit='s', errors='coerce')
                df = df.set_index('date')
            else:
                df.index = pd.to_datetime(df.index)
            # Standardize column names capitalization
            rename_map = {}
            for col in df.columns:
                if col == 'adjustedClose':
                    rename_map[col] = 'Adj Close'
                else:
                    rename_map[col] = col.capitalize()
            df = df.rename(columns=rename_map)
            # Ensure required columns exist
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col not in df.columns:
                    df[col] = np.nan
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].sort_index()
            df = df.tail(n)
            data[sym] = df
        else:
            # No historical data; try to synthesize last bar from quote
            close = r.get('regularMarketPrice')
            if close is None:
                data[sym] = pd.DataFrame()
                continue
            today = pd.to_datetime(dt.date.today())
            df = pd.DataFrame(
                {
                    'Open': [close],
                    'High': [close],
                    'Low': [close],
                    'Close': [close],
                    'Volume': [r.get('regularMarketVolume') or 0],
                },
                index=[today],
            )
            data[sym] = df

    return data


def read_tickers_from_csv(csv_path: str = os.path.join('data', 'portfolio.csv')) -> List[str]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Ticker universe not found: {csv_path}")
    df = pd.read_csv(csv_path)
    if df.shape[1] == 0:
        return []
    raw = df.iloc[:, 0].astype(str).str.strip().tolist()
    tickers: List[str] = []
    for t in raw:
        if not t or t.upper() in ("TICKER",):
            continue
        if t == IBOV:
            continue
        # brapi expects tickers without ".SA"
        t_clean = t
        if t_clean not in tickers:
            tickers.append(t_clean)
    return tickers


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # EMAs
    for p in EMA_PERIODS:
        out[f'EMA_{p}'] = out['Close'].ewm(span=p, adjust=False, min_periods=p).mean()
    # RSI (rolling simple average approximation)
    delta = out['Close'].diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=RSI_PERIOD, min_periods=RSI_PERIOD).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=RSI_PERIOD, min_periods=RSI_PERIOD).mean()
    rs = gain / loss.replace(0, np.nan)
    out[f'RSI_{RSI_PERIOD}'] = 100 - (100 / (1 + rs))
    # Daily return
    out['Return'] = out['Close'].pct_change()
    return out


def round_board_lot_100_half_up(shares_raw: float) -> int:
    if shares_raw is None or shares_raw <= 0:
        return 0
    base_int = int(shares_raw)
    last_two = base_int % 100
    if last_two <= 49:
        rounded = base_int - last_two
    else:
        rounded = base_int + (100 - last_two)
    return max(0, rounded)


def score_symbol(row: pd.Series, ibov_row: pd.Series) -> float:
    # Component 1: Return vs Ibov
    c1 = 0.0
    if pd.notna(row['Return']) and pd.notna(ibov_row['Return']):
        if row['Return'] > ibov_row['Return']:
            c1 = 1.0
        elif row['Return'] < ibov_row['Return']:
            c1 = -1.0

    # Component 2: Close vs EMAs (±0.25 each)
    c2 = 0.0
    for p in EMA_PERIODS:
        ema_val = row.get(f'EMA_{p}', np.nan)
        if pd.notna(ema_val):
            c2 += 0.25 if row['Close'] > ema_val else -0.25

    # Component 3: RSI ±0.25
    c3 = 0.0
    rsi = row.get(f'RSI_{RSI_PERIOD}', np.nan)
    if pd.notna(rsi):
        if rsi > RSI_OVERBOUGHT:
            c3 = 0.25
        elif rsi < RSI_OVERSOLD:
            c3 = -0.25

    return c1 + c2 + c3


def compute_scores(data: Dict[str, pd.DataFrame]) -> Tuple[List[Dict[str, object]], pd.Timestamp]:
    """Compute FuzzyFajuto scores for all symbols on their latest common date with Ibov.
    Returns (scored_list, as_of_date_ibov_latest).
    """
    if IBOV not in data or data[IBOV].empty:
        # If IBOV data is missing, we cannot compute scores relative to IBOV.
        # Return an empty list, but use today's date for as_of to avoid errors.
        print(f"Warning: IBOV data missing or empty, cannot compute relative scores")
        return [], pd.Timestamp(dt.date.today())

    ibov_df_raw = data[IBOV]
    ibov_df_ind = compute_indicators(ibov_df_raw)
    # Normalize to date-only index to avoid minor time/tz misalignments
    ibov_df_ind = ibov_df_ind.copy()
    ibov_df_ind.index = ibov_df_ind.index.normalize()

    scored: List[Dict[str, object]] = []
    symbols_processed = 0
    symbols_with_data = 0

    for sym, df_raw in data.items():
        if sym == IBOV or df_raw.empty:
            continue
        symbols_processed += 1

        df_ind = compute_indicators(df_raw)
        df_ind = df_ind.copy()
        df_ind.index = df_ind.index.normalize()

        # Find latest common date between symbol and IBOV
        common_dates = df_ind.index.intersection(ibov_df_ind.index)
        if common_dates.empty:
            continue
        score_date = common_dates[-1]
        if score_date not in df_ind.index or score_date not in ibov_df_ind.index:
            continue

        row = df_ind.loc[score_date]
        ibrow = ibov_df_ind.loc[score_date]
        score = score_symbol(row, ibrow)
        close = float(row['Close'])
        scored.append({'symbol': sym, 'score': score, 'close': close, 'date': score_date})
        symbols_with_data += 1

    # Use latest IBOV date for file naming if available
    as_of = ibov_df_ind.index[-1] if not ibov_df_ind.empty else pd.Timestamp(dt.date.today())
    
    print(f"Score computation: processed={symbols_processed}, with_scores={symbols_with_data}, total_scores={len(scored)}")
    return scored, as_of


def generate_orders_from_scored(scored: List[Dict[str, object]]) -> List[Dict[str, object]]:
    orders: List[Dict[str, object]] = []
    buys = [
        {'symbol': s['symbol'], 'score': s['score'], 'close': s['close']}
        for s in scored if s['score'] >= BUY_THRESHOLD
    ]
    sells = [
        {'symbol': s['symbol'], 'score': s['score'], 'close': s['close']}
        for s in scored if s['score'] <= SELL_THRESHOLD
    ]
    buys.sort(key=lambda x: (-x['score'], x['symbol']))
    sells.sort(key=lambda x: (x['score'], x['symbol']))
    num_pairs = min(len(buys), len(sells))
    for i in range(num_pairs):
        buy, sell = buys[i], sells[i]
        b_sym = buy['symbol'].replace('.SA', '')
        s_sym = sell['symbol'].replace('.SA', '')
        b_qty = max(100, round_board_lot_100_half_up(NOTIONAL_PER_SYMBOL / buy['close']))
        s_qty = max(100, round_board_lot_100_half_up(NOTIONAL_PER_SYMBOL / sell['close']))
        orders.append({'symbol': b_sym, 'side': 'BUY', 'qty': b_qty, 'price': buy['close'], 'score': buy['score']})
        orders.append({'symbol': s_sym, 'side': 'SELL', 'qty': s_qty, 'price': sell['close'], 'score': sell['score']})
    return orders


def write_scores_log(scored: List[Dict[str, object]], as_of: pd.Timestamp) -> str:
    fname = f"fuzzy_scores_{as_of.strftime('%Y%m%d')}.csv"
    rows = [
        (
            s['symbol'].replace('.SA', ''),
            f"{s['score']:.4f}",
            f"{s['close']:.2f}",
            s['date'].strftime('%Y-%m-%d'),
        )
        for s in scored
    ]
    rows.sort(key=lambda r: r[0])
    with open(fname, 'w', encoding='utf-8') as f:
        f.write('symbol,score,close,date\n')
        for r in rows:
            f.write(','.join(map(str, r)) + '\n')
    return fname


def export_to_tryd_automate(orders: List[Dict[str, object]], output: str = 'automate.xlsx') -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = 'Sheet1'
    ws.append(TRYD_HEADERS)
    today = dt.datetime.now().strftime('%Y-%m-%d')
    client_code = '1234'

    for o in orders:
        if o['side'] == 'BUY':
            row = [
                o['symbol'], client_code, 'Falso', o['qty'], o['qty'], o['qty'],
                float(o['price']),
                None, None, None, None,
                None,
                f"{today} - FuzzyFajuto BUY score={o['score']:.2f}",
            ]
        else:  # SELL
            row = [
                o['symbol'], client_code, None, None, None, None,
                None,
                float(o['price']), o['qty'], o['qty'], o['qty'],
                'Falso',
                f"{today} - FuzzyFajuto SELL score={o['score']:.2f}",
            ]
        ws.append(row)

    wb.save(output)
    return output


def main():
    tickers = read_tickers_from_csv()
    print(f"Processing {len(tickers)} tickers...")
    
    data = fetch_last_n_bars(tickers, n=20)
    successful_fetches = sum(1 for df in data.values() if not df.empty)
    print(f"Successfully fetched data for {successful_fetches}/{len(data)} symbols")
    
    if IBOV not in data or data[IBOV].empty:
        print(f"ERROR: IBOV data not available, cannot compute scores")
        return
    
    scored, as_of = compute_scores(data)
    print(f"Computed {len(scored)} scores for date {as_of.strftime('%Y-%m-%d')}")
    
    log_path = write_scores_log(scored, as_of)
    print(f"Wrote scores to {log_path}")
    
    orders = generate_orders_from_scored(scored)
    print(f"Generated {len(orders)} orders ({len(orders)//2} pairs)")
    
    path = export_to_tryd_automate(orders, 'automate.xlsx')
    print(path)


if __name__ == '__main__':
    main()



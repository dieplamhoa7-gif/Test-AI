"""
backtest_indicators.py — Backtest từng chỉ báo PTKT (TA-Lib) trên MWG.

NGUYÊN TẮC CHỐNG ẢO TƯỞNG HIỆU QUẢ:
1. Long-only: chỉ vào lệnh khi có tín hiệu MUA.
2. Không nhìn tương lai: tín hiệu tại bar t -> vào lệnh giá MỞ CỬA bar t+1 (next-open).
3. So với baseline buy&hold: chỉ báo phải THẮNG việc cứ giữ mới đáng dùng.
4. Phí giao dịch: trừ round-trip cost mỗi lệnh (mặc định 0.3%).
5. Mẫu nhỏ (133 nến tuần): báo cáo số lệnh; <8 lệnh đánh dấu "không đủ mẫu".
6. Hai kiểu thoát: (a) giữ cố định N bar, (b) thoát khi có tín hiệu đảo chiều.

Output: bảng metric mỗi chỉ báo + xếp hạng.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import talib


# =====================================================================
# SINH TÍN HIỆU MUA (=1 tại bar có tín hiệu, ngược lại 0) cho từng chỉ báo
# Mỗi hàm trả Series boolean "có tín hiệu mua tại bar t" (dùng dữ liệu <= t).
# =====================================================================
def signals_rsi(df, low=30):
    rsi = talib.RSI(df["close"].values, 14)
    s = pd.Series(rsi, index=df.index)
    # tín hiệu: RSI cắt LÊN khỏi vùng quá bán
    return (s.shift(1) < low) & (s >= low)


def signals_rsi_cross50(df):
    rsi = pd.Series(talib.RSI(df["close"].values, 14), index=df.index)
    return (rsi.shift(1) < 50) & (rsi >= 50)


def signals_macd(df):
    macd, sig, hist = talib.MACD(df["close"].values, 12, 26, 9)
    h = pd.Series(hist, index=df.index)
    return (h.shift(1) <= 0) & (h > 0)  # MACD cắt lên signal


def signals_golden_cross(df, fast=20, slow=50):
    f = pd.Series(talib.SMA(df["close"].values, fast), index=df.index)
    s = pd.Series(talib.SMA(df["close"].values, slow), index=df.index)
    return (f.shift(1) <= s.shift(1)) & (f > s)


def signals_ema_cross(df, fast=12, slow=26):
    f = pd.Series(talib.EMA(df["close"].values, fast), index=df.index)
    s = pd.Series(talib.EMA(df["close"].values, slow), index=df.index)
    return (f.shift(1) <= s.shift(1)) & (f > s)


def signals_price_above_sma(df, n=20):
    sma = pd.Series(talib.SMA(df["close"].values, n), index=df.index)
    c = df["close"]
    return (c.shift(1) <= sma.shift(1)) & (c > sma)  # giá cắt lên SMA


def signals_stoch(df, low=20):
    k, d = talib.STOCH(df["high"].values, df["low"].values, df["close"].values,
                       fastk_period=14, slowk_period=3, slowd_period=3)
    k = pd.Series(k, index=df.index)
    d = pd.Series(d, index=df.index)
    # %K cắt lên %D trong vùng thấp
    return (k.shift(1) <= d.shift(1)) & (k > d) & (k < low + 30)


def signals_cci(df, low=-100):
    cci = pd.Series(talib.CCI(df["high"].values, df["low"].values, df["close"].values, 14), index=df.index)
    return (cci.shift(1) < low) & (cci >= low)


def signals_adx_di(df):
    plus = pd.Series(talib.PLUS_DI(df["high"].values, df["low"].values, df["close"].values, 14), index=df.index)
    minus = pd.Series(talib.MINUS_DI(df["high"].values, df["low"].values, df["close"].values, 14), index=df.index)
    adx = pd.Series(talib.ADX(df["high"].values, df["low"].values, df["close"].values, 14), index=df.index)
    # +DI cắt lên -DI và ADX > 20 (xu hướng đủ mạnh)
    return (plus.shift(1) <= minus.shift(1)) & (plus > minus) & (adx > 20)


def signals_bbands(df):
    u, m, l = talib.BBANDS(df["close"].values, 20, 2, 2)
    c = df["close"]
    lower = pd.Series(l, index=df.index)
    # giá chạm/thủng dải dưới rồi đóng lại trên (bật từ dải dưới)
    return (c.shift(1) < lower.shift(1)) & (c >= lower)


def signals_williams(df, low=-80):
    wr = pd.Series(talib.WILLR(df["high"].values, df["low"].values, df["close"].values, 14), index=df.index)
    return (wr.shift(1) < low) & (wr >= low)


def signals_mfi(df, low=20):
    mfi = pd.Series(talib.MFI(df["high"].values, df["low"].values, df["close"].values,
                              df["volume"].values, 14), index=df.index)
    return (mfi.shift(1) < low) & (mfi >= low)


def signals_aroon(df):
    down, up = talib.AROON(df["high"].values, df["low"].values, 14)
    u = pd.Series(up, index=df.index)
    d = pd.Series(down, index=df.index)
    return (u.shift(1) <= d.shift(1)) & (u > d)  # Aroon up cắt lên


def signals_sar(df):
    sar = pd.Series(talib.SAR(df["high"].values, df["low"].values, 0.02, 0.2), index=df.index)
    c = df["close"]
    return (c.shift(1) <= sar.shift(1)) & (c > sar)  # giá vượt lên SAR


# tín hiệu THOÁT cho chế độ reversal (tín hiệu ngược lại)
def exit_rsi(df, high=70):
    rsi = pd.Series(talib.RSI(df["close"].values, 14), index=df.index)
    return (rsi.shift(1) > high) & (rsi <= high)

def exit_macd(df):
    _, _, hist = talib.MACD(df["close"].values, 12, 26, 9)
    h = pd.Series(hist, index=df.index)
    return (h.shift(1) >= 0) & (h < 0)

def exit_cross(df, fast, slow, ema=False):
    fn = talib.EMA if ema else talib.SMA
    f = pd.Series(fn(df["close"].values, fast), index=df.index)
    s = pd.Series(fn(df["close"].values, slow), index=df.index)
    return (f.shift(1) >= s.shift(1)) & (f < s)


INDICATORS = {
    "RSI(14) thoát quá bán": (signals_rsi, lambda df: exit_rsi(df)),
    "RSI(14) cắt 50": (signals_rsi_cross50, lambda df: exit_rsi(df, 50)),
    "MACD cắt signal": (signals_macd, exit_macd),
    "Golden Cross SMA20/50": (signals_golden_cross, lambda df: exit_cross(df, 20, 50)),
    "EMA12/26 cross": (signals_ema_cross, lambda df: exit_cross(df, 12, 26, ema=True)),
    "Giá cắt lên SMA20": (signals_price_above_sma, lambda df: ~signals_price_above_sma(df)),
    "Stochastic cross": (signals_stoch, None),
    "CCI(14) thoát -100": (signals_cci, None),
    "ADX +DI/-DI": (signals_adx_di, None),
    "Bollinger bật dải dưới": (signals_bbands, None),
    "Williams %R": (signals_williams, None),
    "MFI(14) thoát quá bán": (signals_mfi, None),
    "Aroon cross": (signals_aroon, None),
    "Parabolic SAR": (signals_sar, None),
}


# =====================================================================
# BACKTEST ENGINE
# =====================================================================
def backtest_fixed(df, entry_sig, horizon, cost=0.003):
    """Vào lệnh next-open sau tín hiệu, giữ `horizon` bar, thoát next-open. Long-only."""
    o = df["open"].values
    n = len(df)
    trades = []
    idxs = np.nonzero(entry_sig.fillna(False).values)[0]
    last_exit = -1
    for i in idxs:
        entry_bar = i + 1            # vào giá mở cửa bar kế tiếp
        exit_bar = entry_bar + horizon
        if entry_bar >= n or exit_bar >= n:
            continue
        if entry_bar <= last_exit:   # không chồng lệnh
            continue
        ep = o[entry_bar]
        xp = o[exit_bar]
        ret = (xp / ep - 1) - cost
        trades.append(ret)
        last_exit = exit_bar
    return np.array(trades)


def backtest_reversal(df, entry_sig, exit_sig, cost=0.003, max_hold=26):
    """Vào next-open sau tín hiệu mua; thoát next-open sau tín hiệu đảo chiều hoặc max_hold."""
    o = df["open"].values
    n = len(df)
    es = entry_sig.fillna(False).values
    xs = exit_sig.fillna(False).values if exit_sig is not None else np.zeros(n, bool)
    trades = []
    i = 0
    while i < n - 1:
        if not es[i]:
            i += 1; continue
        entry_bar = i + 1
        if entry_bar >= n:
            break
        ep = o[entry_bar]
        # tìm điểm thoát
        exit_bar = None
        for j in range(entry_bar, min(entry_bar + max_hold, n - 1)):
            if xs[j]:
                exit_bar = j + 1
                break
        if exit_bar is None:
            exit_bar = min(entry_bar + max_hold, n - 1)
        xp = o[exit_bar]
        trades.append((xp / ep - 1) - cost)
        i = exit_bar  # tiếp tục sau khi thoát
    return np.array(trades)


def metrics(trades, bench_per_trade=None):
    if len(trades) == 0:
        return {"n": 0}
    wins = trades[trades > 0]
    win_rate = len(wins) / len(trades) * 100
    avg = trades.mean() * 100
    med = np.median(trades) * 100
    total = (np.prod(1 + trades) - 1) * 100
    gross_win = trades[trades > 0].sum()
    gross_loss = -trades[trades < 0].sum()
    pf = gross_win / gross_loss if gross_loss > 0 else np.inf
    sharpe = trades.mean() / trades.std() if trades.std() > 0 else 0
    m = {"n": len(trades), "win_rate": round(win_rate, 1), "avg_ret": round(avg, 2),
         "median_ret": round(med, 2), "total_ret": round(total, 1),
         "profit_factor": round(pf, 2) if np.isfinite(pf) else 99.0,
         "sharpe_per_trade": round(sharpe, 3)}
    if bench_per_trade is not None:
        m["edge_vs_bh"] = round(avg - bench_per_trade * 100, 2)
    return m


def buy_hold_per_trade(df, horizon, cost=0.003):
    """Lợi nhuận trung bình của việc mua ngẫu nhiên giữ `horizon` bar — baseline."""
    o = df["open"].values
    n = len(df)
    rets = []
    for i in range(n - horizon - 1):
        rets.append(o[i + horizon] / o[i] - 1 - cost)
    return np.mean(rets) if rets else 0

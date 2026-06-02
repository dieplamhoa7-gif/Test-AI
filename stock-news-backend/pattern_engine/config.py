"""
config.py — Tự động chỉnh tham số detector theo KHUNG THỜI GIAN và ĐỘ DÀI dữ liệu.

Lý do: cùng một detector cần tham số khác nhau giữa daily/weekly/monthly.
Ví dụ pivot distance, lookback cup-handle, ngưỡng impulse flag... đều phụ thuộc
mật độ nến. Lớp này tập trung hóa để mọi detector lấy tham số đã chuẩn hóa,
thay vì hardcode rải rác.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class EngineConfig:
    timeframe: str          # 'daily' | 'weekly' | 'monthly'
    n_bars: int

    # pivot
    pivot_distance: int = 3
    pivot_prom_mult: float = 0.6

    # lookback các pattern (số bar)
    lb_triangle: int = 40
    lb_cup: int = 60
    lb_darvas: int = 30
    lb_rounding: int = 40
    lb_sr: int = 0          # 0 = toàn bộ
    lb_smc: int = 40

    # ngưỡng
    flag_pole: int = 10
    flag_max: int = 12
    flag_impulse: float = 0.10
    double_max_span: int = 60
    target_max_move: float = 0.35
    recent_candles: int = 30
    recent_signals: int = 15

    # forecast
    fc_horizon: int = 20
    fc_fit_window: int = 60

    notes: list = field(default_factory=list)


def build_config(timeframe: str, n_bars: int) -> EngineConfig:
    """Sinh config phù hợp khung + co giãn theo độ dài dữ liệu."""
    cfg = EngineConfig(timeframe=timeframe, n_bars=n_bars)

    if timeframe == "daily":
        # daily: nến dày, pivot cần khoảng cách lớn hơn, lookback dài hơn
        cfg.pivot_distance = 5
        cfg.lb_triangle = 60
        cfg.lb_cup = 120
        cfg.lb_darvas = 40
        cfg.lb_rounding = 60
        cfg.lb_smc = 60
        cfg.flag_pole = 15
        cfg.flag_max = 20
        cfg.double_max_span = 120
        cfg.recent_candles = 60
        cfg.recent_signals = 25
        cfg.fc_horizon = 20
        cfg.fc_fit_window = 90
    elif timeframe == "weekly":
        cfg.pivot_distance = 3
        cfg.lb_triangle = 40
        cfg.lb_cup = 60
        cfg.lb_darvas = 30
        cfg.lb_rounding = 40
        cfg.lb_smc = 40
        cfg.flag_pole = 10
        cfg.flag_max = 12
        cfg.double_max_span = 60
        cfg.recent_candles = 30
        cfg.recent_signals = 15
        cfg.fc_horizon = 20
        cfg.fc_fit_window = 60
    else:  # monthly
        cfg.pivot_distance = 2
        cfg.lb_triangle = 24
        cfg.lb_cup = 36
        cfg.lb_darvas = 18
        cfg.lb_rounding = 24
        cfg.lb_smc = 24
        cfg.flag_pole = 6
        cfg.flag_max = 8
        cfg.double_max_span = 36
        cfg.recent_candles = 18
        cfg.recent_signals = 10
        cfg.fc_horizon = 12
        cfg.fc_fit_window = 36

    # CO GIÃN theo độ dài thực tế: nếu dữ liệu ngắn hơn lookback -> thu nhỏ
    def shrink(v, frac=0.6):
        return max(8, min(v, int(n_bars * frac)))

    cfg.lb_triangle = shrink(cfg.lb_triangle)
    cfg.lb_cup = shrink(cfg.lb_cup, 0.7)
    cfg.lb_darvas = shrink(cfg.lb_darvas, 0.4)
    cfg.lb_rounding = shrink(cfg.lb_rounding)
    cfg.lb_smc = shrink(cfg.lb_smc)
    cfg.double_max_span = min(cfg.double_max_span, n_bars)
    cfg.fc_fit_window = min(cfg.fc_fit_window, n_bars)

    # dữ liệu quá ngắn -> cảnh báo
    if n_bars < 40:
        cfg.notes.append(f"Chỉ {n_bars} nến — nhiều pattern lớn sẽ không đủ dữ liệu để nhận dạng tin cậy.")
    if n_bars < cfg.fc_horizon * 2:
        cfg.fc_horizon = max(5, n_bars // 4)
        cfg.notes.append(f"Rút horizon forecast còn {cfg.fc_horizon} do dữ liệu ngắn.")

    return cfg

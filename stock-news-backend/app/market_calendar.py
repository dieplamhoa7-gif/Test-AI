from __future__ import annotations

from datetime import date, timedelta

# Vietnam / HOSE regular non-trading holidays that are known in advance.
# Use YYYY-MM-DD ISO strings so frontend and backend can share the same list.
VN_MARKET_HOLIDAYS = {
    # 2026 New Year
    "2026-01-01",
    # 2026 Lunar New Year / Tet holiday window
    "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20",
    # Hung Kings Commemoration Day
    "2026-04-27",
    # Reunification Day + International Labour Day holiday window
    "2026-04-30", "2026-05-01",
    # National Day holiday window
    "2026-09-01", "2026-09-02",

    # 2027 New Year
    "2027-01-01",
    # 2027 Lunar New Year / Tet holiday window
    "2027-02-08", "2027-02-09", "2027-02-10", "2027-02-11", "2027-02-12",
    # Hung Kings Commemoration Day
    "2027-04-16",
    # Reunification Day + International Labour Day holiday window
    "2027-04-30", "2027-05-03",
    # National Day holiday window
    "2027-09-02", "2027-09-03",
}


def is_vn_market_workday(day: date) -> bool:
    return day.weekday() < 5 and day.isoformat() not in VN_MARKET_HOLIDAYS


def vn_market_workdays_left(end_day: date, start_day: date | None = None) -> int:
    """Count remaining VN market sessions from today through end_day inclusive.

    If today is a trading day and the warrant's last trading date is today,
    this returns 1 before/through the trading session instead of 0 calendar days.
    """
    today = start_day or date.today()
    if end_day < today:
        return 0
    count = 0
    cur = today
    while cur <= end_day:
        if is_vn_market_workday(cur):
            count += 1
        cur += timedelta(days=1)
    return count

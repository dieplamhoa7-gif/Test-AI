"""Tính trung bình, trung vị, min, max cho danh sách Listing."""
from __future__ import annotations

import statistics
from dataclasses import dataclass

from scraper import Listing


@dataclass
class MetricSummary:
    count: int
    mean: float | None
    median: float | None
    min: float | None
    max: float | None

    def fmt(self, unit: str, decimals: int = 2) -> str:
        if self.count == 0 or self.mean is None or self.median is None:
            return "N/A"
        return (
            f"TB: {self.mean:.{decimals}f}{unit} | "
            f"Trung vị: {self.median:.{decimals}f}{unit} | "
            f"Min: {self.min:.{decimals}f}{unit} | "
            f"Max: {self.max:.{decimals}f}{unit} | "
            f"n={self.count}"
        )


@dataclass
class SourceStats:
    source: str
    price_total: MetricSummary    # tỷ VND
    price_per_m2: MetricSummary   # triệu VND/m2
    area: MetricSummary           # m2


def _summarize(values: list[float]) -> MetricSummary:
    vals = [v for v in values if v is not None and v > 0]
    if not vals:
        return MetricSummary(0, None, None, None, None)
    # Loại outlier theo IQR (nhẹ) nếu đủ mẫu
    if len(vals) >= 5:
        vals_sorted = sorted(vals)
        q1 = statistics.quantiles(vals_sorted, n=4)[0]
        q3 = statistics.quantiles(vals_sorted, n=4)[2]
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        vals = [v for v in vals_sorted if lo <= v <= hi] or vals_sorted
    return MetricSummary(
        count=len(vals),
        mean=statistics.fmean(vals),
        median=statistics.median(vals),
        min=min(vals),
        max=max(vals),
    )


def summarize_source(source: str, listings: list[Listing]) -> SourceStats:
    return SourceStats(
        source=source,
        price_total=_summarize([l.price_total for l in listings if l.price_total]),
        price_per_m2=_summarize([l.price_per_m2 for l in listings if l.price_per_m2]),
        area=_summarize([l.area for l in listings if l.area]),
    )


def summarize_all(buckets: dict[str, list[Listing]]) -> list[SourceStats]:
    return [summarize_source(name, listings) for name, listings in buckets.items()]


def overall_summary(buckets: dict[str, list[Listing]]) -> SourceStats:
    all_listings = [l for ls in buckets.values() for l in ls]
    return summarize_source("Tổng hợp", all_listings)

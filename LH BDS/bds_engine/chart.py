"""Vẽ biểu đồ so sánh giá 3 nguồn → trả về bytes PNG."""
from __future__ import annotations

import io
import logging

import matplotlib
matplotlib.use("Agg")  # backend không cần GUI
import matplotlib.pyplot as plt
import numpy as np

from stats import SourceStats

logger = logging.getLogger(__name__)


def build_comparison_chart(stats_list: list[SourceStats], title: str) -> bytes | None:
    """Tạo biểu đồ cột so sánh giá/m2 và giá tổng giữa 3 nguồn. Trả về PNG bytes."""
    sources = [s.source for s in stats_list]
    if not sources:
        return None

    price_mean = [s.price_per_m2.mean or 0 for s in stats_list]
    price_median = [s.price_per_m2.median or 0 for s in stats_list]
    total_mean = [s.price_total.mean or 0 for s in stats_list]
    total_median = [s.price_total.median or 0 for s in stats_list]

    try:
        fig, axes = plt.subplots(1, 2, figsize=(11, 5))
        fig.suptitle(title, fontsize=12, fontweight="bold")

        x = np.arange(len(sources))
        width = 0.35

        ax1 = axes[0]
        ax1.bar(x - width / 2, price_mean, width, label="Trung bình", color="#2E86AB")
        ax1.bar(x + width / 2, price_median, width, label="Trung vị", color="#A23B72")
        ax1.set_title("Giá/m² (triệu VND/m²)")
        ax1.set_xticks(x)
        ax1.set_xticklabels(sources, rotation=15, ha="right", fontsize=9)
        ax1.legend()
        ax1.grid(axis="y", linestyle="--", alpha=0.4)
        for i, (m, md) in enumerate(zip(price_mean, price_median)):
            if m:
                ax1.text(i - width / 2, m, f"{m:.1f}", ha="center", va="bottom", fontsize=8)
            if md:
                ax1.text(i + width / 2, md, f"{md:.1f}", ha="center", va="bottom", fontsize=8)

        ax2 = axes[1]
        ax2.bar(x - width / 2, total_mean, width, label="Trung bình", color="#F18F01")
        ax2.bar(x + width / 2, total_median, width, label="Trung vị", color="#C73E1D")
        ax2.set_title("Tổng giá (tỷ VND)")
        ax2.set_xticks(x)
        ax2.set_xticklabels(sources, rotation=15, ha="right", fontsize=9)
        ax2.legend()
        ax2.grid(axis="y", linestyle="--", alpha=0.4)
        for i, (m, md) in enumerate(zip(total_mean, total_median)):
            if m:
                ax2.text(i - width / 2, m, f"{m:.2f}", ha="center", va="bottom", fontsize=8)
            if md:
                ax2.text(i + width / 2, md, f"{md:.2f}", ha="center", va="bottom", fontsize=8)

        plt.tight_layout(rect=(0, 0, 1, 0.94))

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()
    except Exception as e:
        logger.exception("Lỗi vẽ chart: %s", e)
        return None

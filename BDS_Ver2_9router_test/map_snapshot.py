"""Tạo ảnh map tĩnh có marker tọa độ gốc và các dự án/khu vực so sánh.

Không phụ thuộc browser/API map ngoài. Dùng sơ đồ tương đối theo lat/lng để bot luôn gửi được ảnh.
"""
from __future__ import annotations

import io
import math
from dataclasses import dataclass
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


@dataclass
class MapPoint:
    name: str
    lat: float
    lng: float
    note: str = ""


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _project_xy(origin_lat: float, origin_lng: float, lat: float, lng: float) -> tuple[float, float]:
    # Equirectangular local projection: x east km, y north km
    y = (lat - origin_lat) * 111.32
    x = (lng - origin_lng) * 111.32 * math.cos(math.radians(origin_lat))
    return x, y


def build_map_snapshot(origin_lat: float, origin_lng: float, points: Iterable[MapPoint], title: str = "Bản đồ so sánh") -> bytes | None:
    pts = list(points)
    try:
        fig, ax = plt.subplots(figsize=(9, 7))
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_facecolor("#eef6f8")
        fig.patch.set_facecolor("white")

        # Origin marker
        ax.scatter([0], [0], s=220, c="#e63946", marker="*", edgecolors="white", linewidths=1.5, zorder=5)
        ax.annotate("Tọa độ cần định giá", (0, 0), xytext=(8, 8), textcoords="offset points", fontsize=10, fontweight="bold", color="#b00020")

        colors = ["#1d4ed8", "#059669", "#7c3aed", "#ea580c", "#0891b2", "#be123c"]
        xs, ys = [0], [0]
        for i, p in enumerate(pts, 1):
            x, y = _project_xy(origin_lat, origin_lng, p.lat, p.lng)
            xs.append(x); ys.append(y)
            dist = haversine_km(origin_lat, origin_lng, p.lat, p.lng)
            color = colors[(i - 1) % len(colors)]
            ax.scatter([x], [y], s=120, c=color, marker="o", edgecolors="white", linewidths=1.2, zorder=4)
            ax.plot([0, x], [0, y], color=color, linestyle="--", alpha=0.35, linewidth=1)
            label = f"{i}. {p.name}\n~{dist:.1f} km"
            ax.annotate(label, (x, y), xytext=(8, 8), textcoords="offset points", fontsize=9, color="#111827")

        max_abs = max([abs(v) for v in xs + ys] + [1.0])
        pad = max(0.8, max_abs * 0.25)
        ax.set_xlim(min(xs) - pad, max(xs) + pad)
        ax.set_ylim(min(ys) - pad, max(ys) + pad)
        ax.axhline(0, color="#94a3b8", linewidth=0.8, alpha=0.7)
        ax.axvline(0, color="#94a3b8", linewidth=0.8, alpha=0.7)
        ax.grid(True, linestyle="--", alpha=0.35)
        ax.set_xlabel("Đông/Tây so với tọa độ gốc (km)")
        ax.set_ylabel("Bắc/Nam so với tọa độ gốc (km)")
        ax.text(0.01, 0.01, "Ảnh sơ đồ tương đối từ tọa độ AI/geocode; cần kiểm chứng khi chốt giá.", transform=ax.transAxes, fontsize=8, color="#475569")
        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()
    except Exception:
        return None


def build_google_maps_url(origin_lat: float, origin_lng: float, points: Iterable[MapPoint]) -> str:
    """Tạo URL Google Maps mở thẳng tọa độ gốc + các điểm so sánh."""
    pts = list(points)[:6]
    query_parts = [f"Tọa độ cần định giá @{origin_lat},{origin_lng}"]
    for i, p in enumerate(pts, 1):
        query_parts.append(f"{i}. {p.name} @{p.lat},{p.lng}")
    # Google Maps search query: ưu tiên mở vùng tọa độ gốc, kèm text các điểm để nhìn map thật.
    from urllib.parse import quote_plus
    q = quote_plus(" | ".join(query_parts))
    return f"https://www.google.com/maps/search/{q}/@{origin_lat},{origin_lng},14z"


def build_google_maps_screenshot(
    origin_lat: float,
    origin_lng: float,
    points: Iterable[MapPoint],
    width: int = 1280,
    height: int = 900,
    timeout_sec: int = 35,
) -> bytes | None:
    """Mở Google Maps thật bằng Chrome headless và chụp screenshot PNG."""
    import os
    import subprocess
    import tempfile
    import time
    from pathlib import Path as _Path

    chrome_candidates = [
        os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
    ]
    browser = next((c for c in chrome_candidates if c and os.path.exists(c)), None)
    if not browser:
        return None

    url = build_google_maps_url(origin_lat, origin_lng, points)
    with tempfile.TemporaryDirectory(prefix="bds_gmaps_") as td:
        out = _Path(td) / "google_maps.png"
        user_data = _Path(td) / "profile"
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-notifications",
            f"--user-data-dir={user_data}",
            f"--window-size={width},{height}",
            f"--screenshot={out}",
            url,
        ]
        try:
            subprocess.run(cmd, check=False, timeout=timeout_sec, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if out.exists() and out.stat().st_size > 5000:
                return out.read_bytes()
        except Exception:
            return None
    return None

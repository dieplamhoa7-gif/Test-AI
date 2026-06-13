"""Tạo bản đồ định giá có pin dự án + nhãn giá/m2.

Ưu tiên tạo HTML Leaflet/OpenStreetMap để giống My Maps: marker + popup/label.
Sau đó dùng Chrome headless chụp thành PNG gửi Telegram.
"""
from __future__ import annotations

import html
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import math


@dataclass
class ValuationMapPoint:
    name: str
    lat: float
    lng: float
    price_per_m2: float | None = None  # triệu/m2
    price_label: str = ""
    price_range: str = ""
    sample_count: int | None = None
    source: str = ""
    note: str = ""


def _chrome_path() -> str | None:
    candidates = [
        os.path.join(os.environ.get("ProgramFiles", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
    ]
    return next((c for c in candidates if c and os.path.exists(c)), None)


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lng2-lng1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.atan2(math.sqrt(a), math.sqrt(1-a))


def _convex_hull_xy(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower = []
    for pt in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], pt) <= 0:
            lower.pop()
        lower.append(pt)
    upper = []
    for pt in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], pt) <= 0:
            upper.pop()
        upper.append(pt)
    return lower[:-1] + upper[:-1]


def _polygon_area_xy(points: list[tuple[float, float]]) -> float:
    if len(points) < 3:
        return 0.0
    area = 0.0
    for i, (x1, y1) in enumerate(points):
        x2, y2 = points[(i + 1) % len(points)]
        area += x1 * y2 - y1 * x2
    return abs(area) / 2.0


def _project_local_m(lat: float, lng: float, lat0: float, lng0: float) -> tuple[float, float]:
    r = 6371000.0
    x = math.radians(lng - lng0) * r * math.cos(math.radians(lat0))
    y = math.radians(lat - lat0) * r
    return x, y


def _unproject_local_m(x: float, y: float, lat0: float, lng0: float) -> tuple[float, float]:
    r = 6371000.0
    lat = lat0 + math.degrees(y / r)
    lng = lng0 + math.degrees(x / (r * math.cos(math.radians(lat0))))
    return lat, lng


def _hull70_view_bounds(origin_lat: float, origin_lng: float, pts: list[ValuationMapPoint], target_ratio: float = 0.70, aspect: float = 1.20):
    # Viewport/hull phải bao gồm cả tọa độ khảo sát + các dự án nghiên cứu.
    all_latlng = [(origin_lat, origin_lng)] + [(p.lat, p.lng) for p in pts]
    if len(all_latlng) < 3:
        return None, None
    lat0 = sum(lat for lat, _ in all_latlng) / len(all_latlng)
    lng0 = sum(lng for _, lng in all_latlng) / len(all_latlng)
    xy = [_project_local_m(lat, lng, lat0, lng0) for lat, lng in all_latlng]
    hull = _convex_hull_xy(xy)
    hull_area = _polygon_area_xy(hull)
    if hull_area <= 1:
        return None, None
    xs = [x for x, _ in xy]; ys = [y for _, y in xy]
    min_x, max_x = min(xs), max(xs); min_y, max_y = min(ys), max(ys)
    cx = (min_x + max_x) / 2; cy = (min_y + max_y) / 2
    map_area = hull_area / target_ratio
    map_w = math.sqrt(map_area * aspect); map_h = map_area / map_w
    bbox_w = max_x - min_x; bbox_h = max_y - min_y
    if map_w < bbox_w:
        map_w = bbox_w; map_h = map_area / map_w
    if map_h < bbox_h:
        map_h = bbox_h; map_w = map_area / map_h
    sw = _unproject_local_m(cx - map_w/2, cy - map_h/2, lat0, lng0)
    ne = _unproject_local_m(cx + map_w/2, cy + map_h/2, lat0, lng0)
    actual_ratio = hull_area / (map_w * map_h) if map_w * map_h else 0
    return [[sw[0], sw[1]], [ne[0], ne[1]]], {
        "hull_area_m2": round(hull_area, 2),
        "map_area_m2": round(map_w * map_h, 2),
        "coverage_ratio": round(actual_ratio, 4),
    }


def build_valuation_map_html(origin_lat: float, origin_lng: float, points: Iterable[ValuationMapPoint], title: str = "Bản đồ so sánh giá") -> str:
    pts = list(points)
    center_lat = (origin_lat + sum(p.lat for p in pts)) / (len(pts) + 1) if pts else origin_lat
    center_lng = (origin_lng + sum(p.lng for p in pts)) / (len(pts) + 1) if pts else origin_lng
    js_points = []
    for i, p in enumerate(pts, 1):
        ppm = p.price_label or (f"{p.price_per_m2:.0f} tr/m²" if p.price_per_m2 else "chưa rõ giá")
        label = f"{i}. {p.name}<br><b>{ppm}</b>"
        popup = f"<b>{i}. {html.escape(p.name)}</b><br>Giá TB: <b>{html.escape(ppm)}</b><br>Biên giá: {html.escape(p.price_range or 'chưa rõ')}<br>Số mẫu: {p.sample_count if p.sample_count is not None else 'chưa rõ'}<br>Nguồn: {html.escape(p.source or 'tham khảo')}<br>{html.escape(p.note or '')}"
        dist = _haversine_km(origin_lat, origin_lng, p.lat, p.lng)
        js_points.append({
            "i": i,
            "name": p.name,
            "lat": p.lat,
            "lng": p.lng,
            "ppm": ppm,
            "distance": f"{dist:.2f} km",
            "label": label,
            "popup": popup,
        })
    import json
    points_json = json.dumps(js_points, ensure_ascii=False)
    map_bounds, hull_stats = _hull70_view_bounds(origin_lat, origin_lng, pts, target_ratio=0.70, aspect=1.20)
    map_bounds_json = json.dumps(map_bounds, ensure_ascii=False)
    hull_stats_json = json.dumps(hull_stats or {}, ensure_ascii=False)
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body {{ margin:0; width:100%; height:100%; font-family: Arial, sans-serif; }}
  #map {{ width:100vw; height:100vh; }}
  .title {{ position:absolute; z-index:999; top:14px; left:54px; background:rgba(255,255,255,.94); padding:10px 14px; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,.28); font-weight:700; font-size:18px; }}
  .legend {{ position:absolute; z-index:999; left:16px; bottom:20px; background:rgba(255,255,255,.94); padding:10px 12px; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,.22); font-size:13px; line-height:1.45; }}
  .price-label {{ background:#fff; border:2px solid #2563eb; border-radius:8px; padding:4px 7px; box-shadow:0 2px 8px rgba(0,0,0,.35); font-size:12px; line-height:1.25; white-space:nowrap; }}
  .origin-dot {{ width:16px; height:16px; border-radius:50%; background:#ef4444; border:3px solid #fff; box-shadow:0 0 0 2px #dc2626,0 2px 10px rgba(0,0,0,.65); }}
  .project-pin {{ display:flex; align-items:center; justify-content:center; width:18px; height:18px; border-radius:50%; background:#facc15; color:#111827; border:2px solid #fff; font-size:10px; font-weight:900; box-shadow:0 2px 8px rgba(0,0,0,.65); }}
  .info-panel {{ position:absolute; z-index:1000; top:72px; right:10px; width:285px; max-height:78vh; overflow:hidden; background:rgba(255,255,255,.94); border-radius:10px; padding:9px 10px; box-shadow:0 3px 14px rgba(0,0,0,.35); font-size:12px; line-height:1.25; }}
  .info-panel h3 {{ margin:0 0 5px 0; font-size:13px; }}
  .info-row {{ border-top:1px solid #e5e7eb; padding:5px 0; }}
  .info-row b {{ color:#111827; }}
  .arrow-svg {{ position:absolute; z-index:999; inset:0; pointer-events:none; }}
</style>
</head>
<body>
<div id="map"></div>
<div class="title">{html.escape(title)}</div>
<div class="legend"><b>Chú thích</b><br>🔴 Tọa độ cần định giá<br>📍 Dự án/khu vực so sánh<br>Giá: giá bán/giá thuê tham khảo</div>
<div class="info-panel" id="infoPanel"><h3>📌 Thông tin dự án</h3><div id="infoRows"></div></div>
<script>
const map = L.map('map', {{ zoomControl: true }}).setView([{center_lat}, {center_lng}], 13);
const imageryLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
  maxZoom: 19,
  attribution: 'Tiles &copy; Esri'
}}).addTo(map);
const labelLayer = L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
  maxZoom: 19,
  attribution: 'Labels &copy; Esri'
}}).addTo(map);
let imageryLoaded = false;
imageryLayer.on('load', () => {{ imageryLoaded = true; }});

const origin = [{origin_lat}, {origin_lng}];
const originIcon = L.divIcon({{ className:'', html:'<div class="origin-dot"></div>', iconSize:[22,22], iconAnchor:[11,11] }});
const originMarker = L.marker(origin, {{icon: originIcon, zIndexOffset:1000}}).addTo(map).bindPopup('<b>Vị trí nghiên cứu</b><br>{origin_lat}, {origin_lng}');

const points = {points_json};
const bounds = [origin];
const infoRows = document.getElementById('infoRows');
points.forEach(p => {{
  bounds.push([p.lat, p.lng]);
  const row = document.createElement('div');
  row.className = 'info-row';
  row.innerHTML = `<b>${{p.i}}. ${{p.name}}</b><br>Giá TB: <b>${{p.ppm}}</b>`;
  infoRows.appendChild(row);
  const icon = L.divIcon({{ className:'', html:`<div class="project-pin">${{p.i}}</div>`, iconSize:[22,22], iconAnchor:[11,11] }});
  L.marker([p.lat, p.lng], {{icon}}).addTo(map).bindPopup(p.popup);
  // Không vẽ đường nối/gạch vàng để ảnh vệ tinh sạch, dễ nhìn.
}});
const hull70Bounds = {map_bounds_json};
const hull70Stats = {hull_stats_json};
if (hull70Bounds && points.length >= 3) {{
  map.fitBounds(hull70Bounds, {{paddingTopLeft:[8,8], paddingBottomRight:[210,12], maxZoom:19}});
}} else if (points.length > 1) {{
  map.fitBounds(bounds, {{paddingTopLeft:[18,18], paddingBottomRight:[230,24], maxZoom:18}});
}} else if (points.length === 1) {{
  map.setView([points[0].lat, points[0].lng], 17);
}} else {{
  map.setView(origin, 18);
}}
function markReadyWhenTilesLoaded() {{
  if (imageryLoaded) {{ window.__MAP_READY__ = true; return; }}
  setTimeout(markReadyWhenTilesLoaded, 500);
}}
setTimeout(markReadyWhenTilesLoaded, 500);
setTimeout(() => {{ window.__MAP_READY__ = true; }}, 10000);
</script>
</body>
</html>"""


def render_valuation_map_png(origin_lat: float, origin_lng: float, points: Iterable[ValuationMapPoint], title: str = "Bản đồ so sánh giá", width: int = 1400, height: int = 950) -> bytes | None:
    browser = _chrome_path()
    if not browser:
        return None
    html_text = build_valuation_map_html(origin_lat, origin_lng, points, title)
    with tempfile.TemporaryDirectory(prefix="valuation_map_") as td:
        td_path = Path(td)
        html_path = td_path / "map.html"
        out = td_path / "map.png"
        html_path.write_text(html_text, encoding="utf-8")
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-notifications",
            f"--user-data-dir={td_path / 'profile'}",
            f"--window-size={width},{height}",
            "--hide-scrollbars",
            "--virtual-time-budget=14000",
            f"--screenshot={out}",
            html_path.as_uri(),
        ]
        try:
            subprocess.run(cmd, check=False, timeout=45, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if out.exists() and out.stat().st_size > 20000:
                return out.read_bytes()
        except Exception:
            return None
    return None

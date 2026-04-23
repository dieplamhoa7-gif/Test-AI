from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import asyncio

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.market_data import get_market_cache, get_market_symbol, get_symbol_catalog, refresh_market_cache
from app.services.scraper import collect_news
from app.services.summarizer import enrich_news_with_ai, summarize_news
from app.store import load_news, merge_news

_market_task: asyncio.Task | None = None


async def _market_data_loop() -> None:
    while True:
        try:
            refresh_market_cache()
        except Exception:
            pass
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _market_task
    refresh_market_cache()
    _market_task = asyncio.create_task(_market_data_loop())
    try:
        yield
    finally:
        if _market_task:
            _market_task.cancel()
            try:
                await _market_task
            except asyncio.CancelledError:
                pass


app = FastAPI(title="VN Stock News Backend", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REFRESH_INTERVAL = timedelta(minutes=15)
_last_refresh_at: datetime | None = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _refresh_news_if_needed(force: bool = False, limit: int = 20) -> list[dict]:
    global _last_refresh_at

    cached_items = load_news()
    now = _utcnow()
    should_refresh = force or not cached_items or _last_refresh_at is None or (now - _last_refresh_at) >= REFRESH_INTERVAL

    if should_refresh:
        try:
            fresh_items = enrich_news_with_ai(collect_news(limit=min(limit, 20)))
            if fresh_items:
                cached_items = merge_news(fresh_items)
                _last_refresh_at = now
        except Exception:
            if cached_items:
                return cached_items
            raise

    return cached_items


class SummarizeResponse(BaseModel):
    total_items: int
    summary: str
    items: list[dict]


DASHBOARD_HTML = """
<!doctype html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>HoaInvest97.vn</title>
  <style>
    :root {
      --bg: #070b14;
      --panel: #101726;
      --panel-2: #151f32;
      --panel-3: #1c2740;
      --line: rgba(151, 170, 214, 0.12);
      --text: #edf2ff;
      --muted: #92a0c0;
      --accent: #64b5ff;
      --accent-2: #4ef0c0;
      --warning: #ffb454;
      --danger: #ff7d7d;
      --shadow: 0 20px 50px rgba(0, 0, 0, .32);
      --radius: 22px;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(83, 123, 255, .18), transparent 28%),
        radial-gradient(circle at top right, rgba(78, 240, 192, .10), transparent 22%),
        linear-gradient(180deg, #060912 0%, #090e18 100%);
      color: var(--text);
    }
    a { color: inherit; text-decoration: none; }
    .shell {
      width: min(1180px, calc(100% - 24px));
      margin: 0 auto;
      padding: 14px 0 40px;
    }
    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px 16px;
      border: 1px solid var(--line);
      background: rgba(9, 14, 24, .85);
      border-radius: 24px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
      position: sticky;
      top: 10px;
      z-index: 20;
    }
    .brand-wrap { display: flex; align-items: center; gap: 14px; }
    .brand-icon {
      width: 46px; height: 46px; border-radius: 16px;
      display: grid; place-items: center;
      background: linear-gradient(135deg, var(--accent), #7a74ff);
      font-size: 20px; font-weight: 800;
      box-shadow: 0 10px 24px rgba(100, 181, 255, .25);
    }
    .brand-text h1 {
      margin: 0; font-size: 24px; line-height: 1.1;
    }
    .brand-text p {
      margin: 4px 0 0; color: var(--muted); font-size: 12px; letter-spacing: .18em;
    }
    .status-pill {
      border: 1px solid rgba(78, 240, 192, .18);
      background: rgba(78, 240, 192, .08);
      color: var(--accent-2);
      padding: 10px 14px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 700;
      white-space: nowrap;
    }
    .ticker {
      overflow: hidden;
      white-space: nowrap;
      margin-top: 14px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(10, 16, 28, .82);
      box-shadow: var(--shadow);
    }
    .ticker-track {
      display: inline-block;
      padding: 12px 0;
      min-width: 100%;
      animation: ticker 28s linear infinite;
    }
    .ticker-item {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-right: 22px;
      color: #c7d4f3;
      font-size: 14px;
    }
    .ticker-item strong { color: #fff; }
    .ticker-up { color: var(--accent-2); }
    @keyframes ticker {
      from { transform: translateX(0); }
      to { transform: translateX(-50%); }
    }
    .hero {
      display: grid;
      grid-template-columns: 1.4fr .9fr;
      gap: 18px;
      margin-top: 18px;
    }
    .panel {
      border: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(14, 20, 34, .92), rgba(12, 18, 31, .92));
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .hero-main {
      padding: 22px;
      min-height: 280px;
      position: relative;
    }
    .eyebrow {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(100, 181, 255, .10);
      color: var(--accent);
      font-size: 12px; font-weight: 700; letter-spacing: .08em;
      text-transform: uppercase;
    }
    .hero-main h2 {
      margin: 18px 0 10px;
      font-size: clamp(28px, 4vw, 42px);
      line-height: 1.08;
      max-width: 720px;
    }
    .hero-main p {
      margin: 0;
      color: #bfcae4;
      font-size: 15px;
      line-height: 1.7;
      max-width: 760px;
      white-space: pre-wrap;
    }
    .hero-actions {
      margin-top: 18px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .chip-btn, .reload-btn {
      border: 1px solid var(--line);
      background: rgba(18, 26, 43, .92);
      color: var(--text);
      border-radius: 999px;
      padding: 11px 14px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
    }
    .chip-btn.active {
      background: linear-gradient(135deg, var(--accent), #7a74ff);
      border-color: transparent;
    }
    .reload-btn {
      background: linear-gradient(135deg, var(--accent), #7a74ff);
      border-color: transparent;
    }
    .hero-side {
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .side-title {
      font-size: 13px;
      color: var(--muted);
      letter-spacing: .14em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }
    .search-box {
      display: flex;
      gap: 10px;
    }
    .search-box input, .search-box select {
      width: 100%;
      background: var(--panel-2);
      color: var(--text);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px 14px;
      outline: none;
    }
    .watchlist, .categories {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .watch-pill, .cat-pill {
      padding: 10px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, .04);
      border: 1px solid var(--line);
      color: #d8e3fb;
      font-size: 13px;
      font-weight: 700;
    }
    .watch-pill span {
      color: var(--accent-2);
      margin-left: 6px;
    }
    .layout {
      display: grid;
      grid-template-columns: 1fr;
      gap: 18px;
      margin-top: 18px;
      align-items: start;
    }
    .feed-panel { padding: 18px; }
    .section-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }
    .section-head h3 { margin: 0; font-size: 22px; }
    .section-head p { margin: 0; color: var(--muted); font-size: 13px; }
    .news-list {
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
    }
    .news-card {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 20px;
      background: linear-gradient(180deg, rgba(21, 31, 50, .95), rgba(14, 20, 34, .95));
      transition: transform .18s ease, border-color .18s ease;
    }
    .news-card:hover {
      transform: translateY(-2px);
      border-color: rgba(100, 181, 255, .28);
    }
    .news-meta {
      display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap;
      color: var(--muted); font-size: 12px;
    }
    .source-tag {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 7px 10px; border-radius: 999px;
      background: rgba(78, 240, 192, .10); color: var(--accent-2);
      border: 1px solid rgba(78, 240, 192, .14); font-weight: 700; text-transform: capitalize;
    }
    .news-title {
      margin: 0; font-size: 20px; line-height: 1.4;
    }
    .news-snippet {
      margin: 0; color: #c3cfe8; font-size: 14px; line-height: 1.75;
      white-space: pre-wrap;
      overflow: visible;
    }
    .news-actions {
      display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;
    }
    .open-link {
      color: var(--accent); font-weight: 700;
    }
    .mini-stat {
      font-size: 12px; color: var(--muted);
    }
    .summary-bar {
      margin-top: 18px;
      padding: 18px;
    }
    .summary-bar .side-summary {
      color: #c9d3ea; font-size: 14px; line-height: 1.8; white-space: pre-wrap;
    }
    .market-panel { margin-top: 18px; padding: 18px; }
    .stock-search-bar { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:14px; }
    .stock-search-bar input {
      flex:1; min-width:220px; background: var(--panel-2); color: var(--text);
      border:1px solid var(--line); border-radius:14px; padding: 12px 14px; outline:none;
    }
    .market-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }
    .market-card {
      border: 1px solid rgba(76, 90, 125, .45);
      border-radius: 16px;
      background: linear-gradient(180deg, rgba(15, 21, 34, .95), rgba(10, 15, 25, .98));
      padding: 14px;
      cursor: pointer;
      transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease;
    }
    .market-card:hover { transform: translateY(-2px); border-color: rgba(100, 181, 255, .4); box-shadow: 0 12px 28px rgba(0,0,0,.22); }
    .market-top { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:8px; }
    .market-type {
      font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted);
      border: 1px solid rgba(151, 170, 214, .18); border-radius: 999px; padding: 4px 8px;
    }
    .market-card strong { display:block; font-size:18px; margin-bottom:2px; }
    .market-price { font-size: 24px; font-weight: 800; margin: 6px 0 4px; }
    .market-change { font-size: 13px; font-weight: 700; }
    .market-up { color: #23c77a; }
    .market-down { color: #ff5b6e; }
    .market-flat { color: #ffd166; }
    .market-meta { color: var(--muted); font-size: 12px; margin-top: 8px; display:flex; justify-content:space-between; gap:8px; }
    .detail-modal {
      position: fixed; inset: 0; background: rgba(3, 7, 16, .82); display: none;
      align-items: center; justify-content: center; padding: 20px; z-index: 99;
    }
    .detail-modal.open { display: flex; }
    .detail-box {
      width: min(1080px, 100%); background: #0b101a; border: 1px solid rgba(92, 110, 148, .32);
      border-radius: 24px; box-shadow: var(--shadow); padding: 0; overflow: hidden;
    }
    .detail-head {
      display:flex; align-items:center; justify-content:space-between; gap:12px; padding: 18px 20px;
      border-bottom: 1px solid rgba(92, 110, 148, .18); background: #0f1522;
    }
    .detail-grid { display:grid; grid-template-columns: 1fr; gap: 0; }
    .stats-box {
      padding: 18px; background: #0d131f;
    }
    .stats-grid { display:grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
    .stat-card {
      border:1px solid rgba(92,110,148,.18); border-radius:14px; padding: 12px; background: rgba(255,255,255,.02);
    }
    .stat-card .label { color: var(--muted); font-size: 12px; margin-bottom: 6px; }
    .stat-card .value { color: #edf2ff; font-size: 16px; font-weight: 800; }
    .muted { color: var(--muted); }
    .error { color: var(--danger); }
    .empty {
      padding: 24px;
      border: 1px dashed var(--line);
      border-radius: 18px;
      color: var(--muted);
      text-align: center;
    }
    @media (max-width: 980px) {
      .hero, .layout, .detail-grid { grid-template-columns: 1fr; }
      .topbar { position: static; }
    }
    @media (max-width: 640px) {
      .shell { width: min(100% - 16px, 1180px); }
      .topbar { padding: 12px; border-radius: 18px; }
      .brand-text h1 { font-size: 21px; }
      .hero-main, .hero-side, .feed-panel, .side-box { padding: 16px; }
      .news-title { font-size: 18px; }
      .ai-grid { grid-template-columns: 1fr; }
      .search-box { flex-direction: column; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <div class="brand-wrap">
        <div class="brand-icon">H</div>
        <div class="brand-text">
          <h1>HoaInvest97.vn</h1>
          <p>HOA INVESTMENT</p>
        </div>
      </div>
      <div class="status-pill" id="apiStatus">Online</div>
    </header>

    <section class="ticker">
      <div class="ticker-track" id="tickerTrack">Đang tải mã quan tâm...</div>
    </section>

    <section class="hero">
      <article class="panel hero-main">
        <div class="eyebrow">Tổng hợp tin nổi bật</div>
        <h2 id="heroTitle">Đang tải dữ liệu thị trường...</h2>
        <p id="heroSummary">Hệ thống đang lấy nội dung từ API /news và /summarize.</p>
        <div class="hero-actions categories" id="categoryBar"></div>
      </article>

    </section>

    <section class="panel summary-bar">
      <div class="side-title">Tóm tắt nhanh</div>
      <div class="side-summary" id="summaryText">Đang tạo tóm tắt...</div>
    </section>

    <section class="panel market-panel">
      <div class="section-head">
        <div>
          <h3>Danh mục quan tâm</h3>
          <p id="marketStatus">Đang tải dữ liệu giá...</p>
        </div>
      </div>
      <div class="stock-search-bar">
        <input id="stockSearchInput" type="text" placeholder="Tìm mã cổ phiếu, ví dụ: VNM, MSN, TCB..." list="stockSearchList" />
        <datalist id="stockSearchList"></datalist>
        <button class="reload-btn" id="stockSearchBtn">Tìm & thêm</button>
      </div>
      <div class="market-grid" id="marketGrid"></div>
    </section>

    <section class="layout">
      <main class="panel feed-panel">
        <div class="section-head">
          <div>
            <h3>Dòng tin</h3>
            <p id="statusText">Đang tải...</p>
          </div>
        </div>
        <div class="news-list" id="newsList"></div>
        <div class="section-head" style="margin-top:16px;">
          <div class="categories" style="align-items:center;">
            <button class="chip-btn" id="prevPageBtn">← Lùi</button>
            <input id="pageInput" type="number" min="1" value="1" style="width:90px;background:var(--panel-2);color:var(--text);border:1px solid var(--line);border-radius:12px;padding:10px 12px;" />
            <button class="chip-btn" id="goPageBtn">Đi tới</button>
            <button class="chip-btn" id="nextPageBtn">Tiếp →</button>
          </div>
          <p id="pageInfo">Trang 1/1</p>
        </div>
      </main>
    </section>
  </div>

  <div class="detail-modal" id="detailModal">
    <div class="detail-box">
      <div class="detail-head">
        <div>
          <h3 id="detailTitle" style="margin:0;">Chi tiết mã</h3>
          <p id="detailSub" class="muted" style="margin:6px 0 0;">Đang tải...</p>
        </div>
        <button class="chip-btn" id="closeDetailBtn">Đóng</button>
      </div>
      <div class="detail-grid">
        <div class="stats-box" id="detailStats"></div>
      </div>
    </div>
  </div>

  <script>
    const API_BASE = '';
    const AUTO_REFRESH_MS = 15 * 60 * 1000;
    const DEFAULT_CATEGORIES = ['Tổng hợp', 'Chứng khoán', 'Ngân hàng', 'Bất động sản', 'Pháp luật', 'Chính trị', 'Khác'];

    const elements = {
      apiStatus: document.getElementById('apiStatus'),
      tickerTrack: document.getElementById('tickerTrack'),
      categoryBar: document.getElementById('categoryBar'),
      heroTitle: document.getElementById('heroTitle'),
      heroSummary: document.getElementById('heroSummary'),
      statusText: document.getElementById('statusText'),
      newsList: document.getElementById('newsList'),
      summaryText: document.getElementById('summaryText'),
      marketStatus: document.getElementById('marketStatus'),
      marketGrid: document.getElementById('marketGrid'),
      stockSearchInput: document.getElementById('stockSearchInput'),
      stockSearchBtn: document.getElementById('stockSearchBtn'),
      stockSearchList: document.getElementById('stockSearchList'),
      detailModal: document.getElementById('detailModal'),
      detailTitle: document.getElementById('detailTitle'),
      detailSub: document.getElementById('detailSub'),
      detailStats: document.getElementById('detailStats'),
      closeDetailBtn: document.getElementById('closeDetailBtn'),
      prevPageBtn: document.getElementById('prevPageBtn'),
      nextPageBtn: document.getElementById('nextPageBtn'),
      goPageBtn: document.getElementById('goPageBtn'),
      pageInput: document.getElementById('pageInput'),
      pageInfo: document.getElementById('pageInfo')
    };

    const PAGE_SIZE = 5;
    let allItems = [];
    let filteredItems = [];
    let activeCategory = 'Tổng hợp';
    let autoRefreshTimer = null;
    let currentPage = 1;
    let marketItems = [];
    let watchSymbols = [];

    function escapeHtml(text = '') {
      return String(text)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
    }

    function formatTime(value) {
      if (!value) return 'Không rõ thời gian';
      const normalized = String(value).replace('T', ' ').replace('Z', '');
      return normalized;
    }

    function inferCategory(item) {
      if (item.category) return item.category;
      const text = `${item.title || ''} ${item.snippet || ''}`.toLowerCase();
      if (/ngân hàng|bank|tcb|vcb|mbb|acb|bid/.test(text)) return 'Ngân hàng';
      if (/bất động sản|địa ốc|vinhome|vic|vhm|nvl|kdh/.test(text)) return 'Bất động sản';
      if (/phạt|khởi tố|vi phạm|điều tra|pháp luật/.test(text)) return 'Pháp luật';
      if (/quốc hội|chính phủ|chính trị|bộ ngành/.test(text)) return 'Chính trị';
      if (/cổ phiếu|chứng khoán|vn-index|sàn|niêm yết|hpg|ssi|fpt|mwg/.test(text)) return 'Chứng khoán';
      return 'Khác';
    }

    function renderCategories() {
      elements.categoryBar.innerHTML = DEFAULT_CATEGORIES.map(cat => `
        <button class="chip-btn ${cat === activeCategory ? 'active' : ''}" data-cat="${escapeHtml(cat)}">${escapeHtml(cat)}</button>
      `).join('');

      elements.categoryBar.querySelectorAll('[data-cat]').forEach(btn => {
        btn.addEventListener('click', () => {
          activeCategory = btn.dataset.cat;
          renderCategories();
          applyFilters();
        });
      });
    }

    function formatNumber(value, digits = 2) {
      const n = Number(value);
      if (Number.isNaN(n)) return '-';
      return n.toLocaleString('vi-VN', { minimumFractionDigits: digits, maximumFractionDigits: digits });
    }

    function formatVolume(value) {
      const n = Number(value || 0);
      if (!n) return '-';
      return n.toLocaleString('vi-VN');
    }

    function getChangeClass(change) {
      const n = Number(change || 0);
      if (n > 0) return 'market-up';
      if (n < 0) return 'market-down';
      return 'market-flat';
    }

    function renderMarket(payload) {
      const incoming = Array.isArray(payload) ? payload : (Array.isArray(payload?.items) ? payload.items : []);
      if (!watchSymbols.length) {
        watchSymbols = incoming.map(item => String(item.ticker || '').toUpperCase()).filter(Boolean);
      }
      const merged = [...marketItems];
      incoming.forEach(item => {
        const idx = merged.findIndex(x => x.ticker === item.ticker);
        if (idx >= 0) merged[idx] = item;
        else merged.push(item);
      });
      marketItems = merged.filter(item => watchSymbols.includes(String(item.ticker || '').toUpperCase()));
      const updatedAt = payload?.updatedAt ? formatTime(payload.updatedAt) : null;
      elements.marketStatus.textContent = marketItems.length
        ? `Cập nhật ${marketItems.length} mã${updatedAt ? ` • ${updatedAt}` : ''}`
        : 'Không có dữ liệu giá';
      elements.marketGrid.innerHTML = marketItems.map(item => {
        const cls = getChangeClass(item.changePct);
        const sign = Number(item.changePct || 0) > 0 ? '+' : '';
        return `
          <div class="market-card" data-ticker="${escapeHtml(item.ticker || '')}">
            <div class="market-top">
              <strong>${escapeHtml(item.ticker || '')}</strong>
              <span class="market-type">${escapeHtml(item.type || 'stock')}</span>
            </div>
            <div class="market-price ${cls}">${escapeHtml(formatNumber(item.price))}</div>
            <div class="market-change ${cls}">${sign}${escapeHtml(formatNumber(item.changePct))}%</div>
            <div class="market-meta"><span>KL</span><span>${escapeHtml(formatVolume(item.volume))}</span></div>
          </div>
        `;
      }).join('');

      const tickerItems = [...marketItems, ...marketItems].slice(0, 12).map(item => {
        const cls = getChangeClass(item.changePct);
        const sign = Number(item.changePct || 0) > 0 ? '+' : '';
        return `<span class="ticker-item"><strong>${escapeHtml(item.ticker)}</strong> ${escapeHtml(formatNumber(item.price))} <span class="${cls}">${sign}${escapeHtml(formatNumber(item.changePct))}%</span></span>`;
      }).join('');
      if (tickerItems) elements.tickerTrack.innerHTML = tickerItems;

      elements.marketGrid.querySelectorAll('[data-ticker]').forEach(card => {
        card.addEventListener('click', () => openDetail(card.dataset.ticker));
      });
    }

    function computeFrameTechnical(item, frame) {
      const tech = item.technical || {};
      const multipliers = {
        hour: { macd: 0.65, rsi: 0.96, adx: 0.9, support: 1, resistance: 1 },
        day: { macd: 1, rsi: 1, adx: 1, support: 1, resistance: 1 },
        week: { macd: 1.1, rsi: 1.02, adx: 1.15, support: 1, resistance: 1 },
        month: { macd: 1.2, rsi: 1.04, adx: 1.25, support: 1, resistance: 1 },
      };
      const m = multipliers[frame] || multipliers.day;
      return {
        trend: String(tech.trend ?? 'Trung tính'),
        trendStrength: String(tech.trendStrength ?? '-'),
        rsi: Math.max(0, Math.min(100, Number(tech.relativeStrength ?? tech.rsi14 ?? 50) * m.rsi)),
        macd: Number(tech.macd ?? 0) * m.macd,
        signal: Number(tech.signal ?? 0) * m.macd,
        histogram: Number(tech.histogram ?? 0) * m.macd,
        adx14: Number(tech.adx14 ?? 0) * m.adx,
        plusDi: Number(tech.plusDi ?? 0),
        minusDi: Number(tech.minusDi ?? 0),
        ma20: Number(tech.ma20 ?? 0),
        ma50: Number(tech.ma50 ?? 0),
        ma200: Number(tech.ma200 ?? 0),
        buyPrice: Number(tech.buyPrice ?? tech.supportDay ?? 0),
        sellPrice: Number(tech.sellPrice ?? tech.resistanceDay ?? 0),
      };
    }

    function openDetail(ticker) {
      const item = marketItems.find(x => x.ticker === ticker);
      if (!item) return;
      const cls = getChangeClass(item.changePct);
      const sign = Number(item.changePct || 0) > 0 ? '+' : '';
      elements.detailTitle.innerHTML = `${escapeHtml(item.ticker)} <span class="${cls}">${escapeHtml(formatNumber(item.price))}</span>`;
      const tech = item.technical || {};

      const renderFrame = (frame = 'day') => {
        const framed = computeFrameTechnical(item, frame);
        const frameLabel = ({ hour: 'Giờ', day: 'Ngày', week: 'Tuần', month: 'Tháng' })[frame] || 'Ngày';
        elements.detailSub.textContent = `Biến động ${sign}${formatNumber(item.changePct)}% • Khối lượng ${formatVolume(item.volume)} • Khung ${frameLabel}`;
        const recommendation = String(tech.strategy || `Cổ phiếu đang ${String(framed.trend).toLowerCase()}. Mua gần hỗ trợ và bán gần kháng cự.`);

        elements.detailStats.innerHTML = `
          <div style="margin-bottom:14px; display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap;">
            <div>
              <div class="muted" style="font-size:12px; margin-bottom:6px;">Tổng quan PTKT</div>
              <div style="font-size:28px; font-weight:800;" class="${cls}">${escapeHtml(formatNumber(item.price))}</div>
              <div class="${cls}" style="font-weight:700; margin-top:4px;">${sign}${escapeHtml(formatNumber(item.changePct))}%</div>
            </div>
            <div class="categories">
              <button class="chip-btn ${frame === 'hour' ? 'active' : ''}" data-frame="hour">Giờ</button>
              <button class="chip-btn ${frame === 'day' ? 'active' : ''}" data-frame="day">Ngày</button>
              <button class="chip-btn ${frame === 'week' ? 'active' : ''}" data-frame="week">Tuần</button>
              <button class="chip-btn ${frame === 'month' ? 'active' : ''}" data-frame="month">Tháng</button>
            </div>
          </div>
          <div class="stat-card" style="margin-bottom:12px; grid-column: 1 / -1;">
            <div class="label">Chiến lược đầu tư</div>
            <div class="value" style="font-size:14px; font-weight:600; line-height:1.6;">${escapeHtml(recommendation)}</div>
          </div>
          <div class="stats-grid">
            <div class="stat-card"><div class="label">Xu hướng</div><div class="value">${escapeHtml(String(framed.trend))}</div></div>
            <div class="stat-card"><div class="label">Sức mạnh xu hướng</div><div class="value">${escapeHtml(String(framed.trendStrength))}</div></div>
            <div class="stat-card"><div class="label">Giá múc</div><div class="value">${escapeHtml(formatNumber(framed.buyPrice))}</div></div>
            <div class="stat-card"><div class="label">Giá bán</div><div class="value">${escapeHtml(formatNumber(framed.sellPrice))}</div></div>
            <div class="stat-card"><div class="label">Khối lượng</div><div class="value">${escapeHtml(formatVolume(item.volume))}</div></div>
            <div class="stat-card"><div class="label">RSI</div><div class="value">${escapeHtml(formatNumber(framed.rsi))}</div></div>
            <div class="stat-card"><div class="label">MACD</div><div class="value">${escapeHtml(formatNumber(framed.macd, 3))}</div></div>
            <div class="stat-card"><div class="label">Signal</div><div class="value">${escapeHtml(formatNumber(framed.signal, 3))}</div></div>
            <div class="stat-card"><div class="label">Histogram</div><div class="value">${escapeHtml(formatNumber(framed.histogram, 3))}</div></div>
            <div class="stat-card"><div class="label">ADX14</div><div class="value">${escapeHtml(formatNumber(framed.adx14))}</div></div>
            <div class="stat-card"><div class="label">+DI</div><div class="value">${escapeHtml(formatNumber(framed.plusDi))}</div></div>
            <div class="stat-card"><div class="label">-DI</div><div class="value">${escapeHtml(formatNumber(framed.minusDi))}</div></div>
            <div class="stat-card"><div class="label">MA20</div><div class="value">${escapeHtml(formatNumber(framed.ma20))}</div></div>
            <div class="stat-card"><div class="label">MA50</div><div class="value">${escapeHtml(formatNumber(framed.ma50))}</div></div>
            <div class="stat-card"><div class="label">MA200</div><div class="value">${escapeHtml(formatNumber(framed.ma200))}</div></div>
            <div class="stat-card"><div class="label">Tham chiếu</div><div class="value">${escapeHtml(formatNumber(tech.reference ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Mở cửa</div><div class="value">${escapeHtml(formatNumber(tech.open ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Cao nhất</div><div class="value">${escapeHtml(formatNumber(tech.high ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Thấp nhất</div><div class="value">${escapeHtml(formatNumber(tech.low ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Giá TB</div><div class="value">${escapeHtml(formatNumber(tech.avg ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Pivot ngày</div><div class="value">${escapeHtml(formatNumber(tech.pivotDay ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Hỗ trợ ngày S1</div><div class="value">${escapeHtml(formatNumber(tech.supportDay ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Kháng cự ngày R1</div><div class="value">${escapeHtml(formatNumber(tech.resistanceDay ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Hỗ trợ ngày S2</div><div class="value">${escapeHtml(formatNumber(tech.supportDay2 ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Kháng cự ngày R2</div><div class="value">${escapeHtml(formatNumber(tech.resistanceDay2 ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Pivot tuần</div><div class="value">${escapeHtml(formatNumber(tech.pivotWeek ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Hỗ trợ tuần S1</div><div class="value">${escapeHtml(formatNumber(tech.supportWeek ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Kháng cự tuần R1</div><div class="value">${escapeHtml(formatNumber(tech.resistanceWeek ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Hỗ trợ tuần S2</div><div class="value">${escapeHtml(formatNumber(tech.supportWeek2 ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Kháng cự tuần R2</div><div class="value">${escapeHtml(formatNumber(tech.resistanceWeek2 ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Pivot tháng</div><div class="value">${escapeHtml(formatNumber(tech.pivotMonth ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Hỗ trợ tháng S1</div><div class="value">${escapeHtml(formatNumber(tech.supportMonth ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Kháng cự tháng R1</div><div class="value">${escapeHtml(formatNumber(tech.resistanceMonth ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Hỗ trợ tháng S2</div><div class="value">${escapeHtml(formatNumber(tech.supportMonth2 ?? 0))}</div></div>
            <div class="stat-card"><div class="label">Kháng cự tháng R2</div><div class="value">${escapeHtml(formatNumber(tech.resistanceMonth2 ?? 0))}</div></div>
          </div>
        `;

        elements.detailStats.querySelectorAll('[data-frame]').forEach(btn => {
          btn.addEventListener('click', () => renderFrame(btn.dataset.frame));
        });
      };

      renderFrame('day');
      elements.detailModal.classList.add('open');
    }

    function renderNews(items) {
      filteredItems = items;
      const totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
      if (currentPage > totalPages) currentPage = totalPages;
      if (currentPage < 1) currentPage = 1;
      elements.pageInput.value = currentPage;
      elements.pageInfo.textContent = `Trang ${currentPage}/${totalPages}`;

      if (!items.length) {
        elements.newsList.innerHTML = '<div class="empty">Không có tin phù hợp với bộ lọc hiện tại.</div>';
        elements.statusText.textContent = 'Không có dữ liệu hiển thị';
        return;
      }

      const start = (currentPage - 1) * PAGE_SIZE;
      const pagedItems = items.slice(start, start + PAGE_SIZE);
      elements.statusText.textContent = `Hiển thị ${pagedItems.length}/${items.length} tin`;
      elements.newsList.innerHTML = pagedItems.map((item, index) => `
        <article class="news-card">
          <div class="news-meta">
            <span class="source-tag">${escapeHtml(item.source || 'unknown')}</span>
            <span>${escapeHtml(formatTime(item.published_at || item.fetched_at))}</span>
          </div>
          <h3 class="news-title">${escapeHtml(item.title || 'Không có tiêu đề')}</h3>
          <p class="news-snippet">${escapeHtml(item.snippet || '')}</p>
          <div class="news-actions">
            <a class="open-link" href="${escapeHtml(item.url || '#')}" target="_blank" rel="noreferrer">Đọc bài gốc</a>
            <div class="mini-stat">Tin #${start + index + 1} • ${escapeHtml(inferCategory(item))}</div>
          </div>
        </article>
      `).join('');
    }

    function applyFilters(resetPage = true) {
      let items = [...allItems];

      if (resetPage) currentPage = 1;

      if (activeCategory !== 'Tổng hợp') {
        items = items.filter(item => inferCategory(item) === activeCategory);
      }

      renderNews(items);
    }

    function updateHero(newsData, summaryData) {
      const first = newsData.items?.[0];
      elements.heroTitle.textContent = first?.title || 'Chưa có tiêu đề nổi bật';
      elements.heroSummary.textContent = summaryData.summary || 'Chưa có tóm tắt thị trường.';
      elements.summaryText.textContent = summaryData.summary || 'Chưa có tóm tắt thị trường.';
    }

    function scheduleAutoRefresh() {
      if (autoRefreshTimer) clearTimeout(autoRefreshTimer);
      autoRefreshTimer = setTimeout(() => loadData(true), AUTO_REFRESH_MS);
    }

    async function searchStockCatalog() {
      const q = (elements.stockSearchInput.value || '').trim();
      if (!q) {
        elements.stockSearchList.innerHTML = '';
        return;
      }
      try {
        const res = await fetch(`${API_BASE}/market-symbols?query=${encodeURIComponent(q)}&limit=20`, { cache: 'no-store' });
        if (!res.ok) return;
        const items = await res.json();
        elements.stockSearchList.innerHTML = items.map(item => `<option value="${escapeHtml(item.symbol)}">${escapeHtml(item.name || '')}</option>`).join('');
      } catch (_) {}
    }

    async function addStockToWatchlist() {
      const symbol = (elements.stockSearchInput.value || '').trim().toUpperCase();
      if (!symbol) return;
      elements.stockSearchBtn.textContent = 'Đang thêm...';
      try {
        const res = await fetch(`${API_BASE}/market-data/${encodeURIComponent(symbol)}?ts=${Date.now()}`, { cache: 'no-store' });
        if (!res.ok) throw new Error('Không tìm thấy mã');
        const item = await res.json();
        if (!watchSymbols.includes(symbol)) watchSymbols.unshift(symbol);
        renderMarket([item]);
        elements.stockSearchInput.value = '';
      } catch (_) {
        elements.marketStatus.textContent = `Không tìm thấy mã ${symbol}`;
      } finally {
        elements.stockSearchBtn.textContent = 'Tìm & thêm';
      }
    }

    async function loadData(isAutoRefresh = false, forceRefresh = false) {
      const limit = 200;
      const ts = Date.now();
      const refreshFlag = forceRefresh || isAutoRefresh;
      elements.apiStatus.textContent = isAutoRefresh ? 'Tự động cập nhật' : 'Đang tải';
      elements.statusText.textContent = isAutoRefresh ? 'Đang tự động cập nhật dữ liệu...' : 'Đang đồng bộ dữ liệu...';
      elements.summaryText.textContent = 'Đang tạo tóm tắt...';
      try {
        const marketRes = await fetch(`${API_BASE}/market-data?ts=${ts}`, { cache: 'no-store' });
        if (marketRes.ok) {
          const marketData = await marketRes.json();
          renderMarket(marketData);
        }

        const newsRes = await fetch(`${API_BASE}/news?limit=${limit}&refresh=${refreshFlag}&ts=${ts}`, { cache: 'no-store' });
        if (!newsRes.ok) throw new Error('News API lỗi');
        const newsData = await newsRes.json();

        allItems = Array.isArray(newsData.items) ? newsData.items : [];
        currentPage = 1;
        applyFilters();

        let summaryData = { summary: '' };
        try {
          const summaryRes = await fetch(`${API_BASE}/summarize?limit=${limit}&max_chars=2200&refresh=false&ts=${ts}`, { cache: 'no-store' });
          if (summaryRes.ok) {
            summaryData = await summaryRes.json();
          }
        } catch (_) {}

        updateHero(newsData, summaryData);
        elements.apiStatus.textContent = 'Online';
        scheduleAutoRefresh();
      } catch (error) {
        allItems = [];
        elements.apiStatus.textContent = 'Offline';
        elements.statusText.innerHTML = '<span class="error">Lỗi tải dữ liệu từ API.</span>';
        elements.summaryText.textContent = 'Không tải được tóm tắt.';
        elements.newsList.innerHTML = '<div class="empty error">Không thể kết nối API.</div>';
        scheduleAutoRefresh();
      }
    }

    elements.stockSearchBtn.addEventListener('click', addStockToWatchlist);
    elements.stockSearchInput.addEventListener('input', searchStockCatalog);
    elements.stockSearchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') addStockToWatchlist();
    });
    elements.prevPageBtn.addEventListener('click', () => { currentPage -= 1; renderNews(filteredItems); });
    elements.nextPageBtn.addEventListener('click', () => { currentPage += 1; renderNews(filteredItems); });
    elements.goPageBtn.addEventListener('click', () => {
      currentPage = Number(elements.pageInput.value) || 1;
      renderNews(filteredItems);
    });

    elements.closeDetailBtn.addEventListener('click', () => elements.detailModal.classList.remove('open'));
    elements.detailModal.addEventListener('click', (e) => {
      if (e.target === elements.detailModal) elements.detailModal.classList.remove('open');
    });

    renderCategories();
    loadData();
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(DASHBOARD_HTML)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/news")
def news(limit: int = Query(default=20, ge=1, le=100), refresh: bool = Query(default=False)):
    items = _refresh_news_if_needed(force=refresh, limit=limit)
    return {"total_items": len(items), "items": items[:limit]}


@app.get("/summarize", response_model=SummarizeResponse)
def summarize(limit: int = Query(default=20, ge=1, le=100), max_chars: int = Query(default=2200, ge=300, le=6000), refresh: bool = Query(default=False)):
    items = _refresh_news_if_needed(force=refresh, limit=limit)[:limit]
    summary = summarize_news(items, max_chars=max_chars)
    return {"total_items": len(items), "summary": summary, "items": items}


@app.get("/market-data")
def market_data():
    data = get_market_cache()
    return data["items"]


@app.get("/market-data/{symbol}")
def market_symbol(symbol: str):
    return get_market_symbol(symbol)


@app.get("/market-symbols")
def market_symbols(query: str = Query(default=""), limit: int = Query(default=20, ge=1, le=100)):
    return get_symbol_catalog(query=query, limit=limit)

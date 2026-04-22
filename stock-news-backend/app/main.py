from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.services.scraper import collect_news
from app.services.summarizer import enrich_news_with_ai, summarize_news

app = FastAPI(title="VN Stock News Backend", version="0.1.0")


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
  <title>HOA Investment News</title>
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
      grid-template-columns: 1fr 320px;
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
      display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
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
    .side-stack {
      display: flex; flex-direction: column; gap: 18px;
    }
    .side-box { padding: 18px; }
    .big-number {
      font-size: 34px; font-weight: 800; margin: 6px 0 4px;
    }
    .side-summary {
      color: #c9d3ea; font-size: 14px; line-height: 1.7; white-space: pre-wrap;
    }
    .ai-grid {
      display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
    }
    .ai-card {
      border: 1px solid var(--line);
      border-radius: 18px;
      background: rgba(255,255,255,.03);
      padding: 14px;
    }
    .ai-card strong { display: block; margin-bottom: 6px; }
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
      .hero, .layout { grid-template-columns: 1fr; }
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
          <h1>Cập Nhật Tin Nhanh</h1>
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

      <aside class="panel hero-side">
        <div>
          <div class="side-title">Tìm kiếm</div>
          <div class="search-box">
            <input id="searchInput" type="text" placeholder="Tìm tiêu đề, công ty, nguồn..." />
            <select id="limitInput">
              <option value="6">6</option>
              <option value="10" selected>10</option>
              <option value="15">15</option>
              <option value="20">20</option>
            </select>
          </div>
        </div>

        <div>
          <div class="side-title">Danh mục quan tâm</div>
          <div class="watchlist" id="watchlist"></div>
        </div>

        <div>
          <div class="side-title">Điều khiển</div>
          <div class="categories">
            <button class="reload-btn" id="reloadBtn">Làm mới dữ liệu</button>
          </div>
        </div>
      </aside>
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
      </main>

      <aside class="side-stack">
        <section class="panel side-box">
          <div class="side-title">Tổng số tin</div>
          <div class="big-number" id="totalCount">0</div>
          <div class="muted">Đồng bộ trực tiếp từ backend FastAPI.</div>
        </section>

        <section class="panel side-box">
          <div class="side-title">Hệ thống AI</div>
          <div class="ai-grid">
            <div class="ai-card">
              <strong>Model</strong>
              <div class="muted">Router API</div>
            </div>
            <div class="ai-card">
              <strong>Frontend</strong>
              <div class="muted">HTML + CSS + JS</div>
            </div>
          </div>
        </section>

        <section class="panel side-box">
          <div class="side-title">Tóm tắt nhanh</div>
          <div class="side-summary" id="summaryText">Đang tạo tóm tắt...</div>
        </section>
      </aside>
    </section>
  </div>

  <script>
    const API_BASE = '';
    const AUTO_REFRESH_MS = 15 * 60 * 1000;
    const DEFAULT_CATEGORIES = ['Tổng hợp', 'Chứng khoán', 'Ngân hàng', 'Bất động sản', 'Pháp luật', 'Chính trị', 'Khác'];
    const WATCHLIST = [
      { code: 'FPT', price: '148.50', change: '+2.41%' },
      { code: 'MWG', price: '68.12', change: '+0.92%' },
      { code: 'VIC', price: '43.41', change: '+0.95%' },
      { code: 'HPG', price: '31.71', change: '+2.29%' },
      { code: 'VCB', price: '98.48', change: '+1.53%' },
      { code: 'SSI', price: '39.20', change: '+2.62%' }
    ];

    const elements = {
      apiStatus: document.getElementById('apiStatus'),
      tickerTrack: document.getElementById('tickerTrack'),
      categoryBar: document.getElementById('categoryBar'),
      searchInput: document.getElementById('searchInput'),
      limitInput: document.getElementById('limitInput'),
      reloadBtn: document.getElementById('reloadBtn'),
      heroTitle: document.getElementById('heroTitle'),
      heroSummary: document.getElementById('heroSummary'),
      totalCount: document.getElementById('totalCount'),
      statusText: document.getElementById('statusText'),
      newsList: document.getElementById('newsList'),
      summaryText: document.getElementById('summaryText'),
      watchlist: document.getElementById('watchlist')
    };

    let allItems = [];
    let activeCategory = 'Tổng hợp';
    let autoRefreshTimer = null;

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

    function renderWatchlist() {
      elements.watchlist.innerHTML = WATCHLIST.map(item => `
        <div class="watch-pill">${item.code} ${item.price} <span>${item.change}</span></div>
      `).join('');

      const tickerItems = [...WATCHLIST, ...WATCHLIST].map(item => `
        <span class="ticker-item"><strong>${item.code}</strong> ${item.price} <span class="ticker-up">${item.change}</span></span>
      `).join('');
      elements.tickerTrack.innerHTML = tickerItems;
    }

    function renderNews(items) {
      elements.totalCount.textContent = items.length;
      if (!items.length) {
        elements.newsList.innerHTML = '<div class="empty">Không có tin phù hợp với bộ lọc hiện tại.</div>';
        elements.statusText.textContent = 'Không có dữ liệu hiển thị';
        return;
      }

      elements.statusText.textContent = `Hiển thị ${items.length} tin`;
      elements.newsList.innerHTML = items.map((item, index) => `
        <article class="news-card">
          <div class="news-meta">
            <span class="source-tag">${escapeHtml(item.source || 'unknown')}</span>
            <span>${escapeHtml(formatTime(item.published_at || item.fetched_at))}</span>
          </div>
          <h3 class="news-title">${escapeHtml(item.title || 'Không có tiêu đề')}</h3>
          <p class="news-snippet">${escapeHtml(item.snippet || '')}</p>
          <div class="news-actions">
            <a class="open-link" href="${escapeHtml(item.url || '#')}" target="_blank" rel="noreferrer">Đọc bài gốc</a>
            <div class="mini-stat">Tin #${index + 1} • ${escapeHtml(inferCategory(item))}</div>
          </div>
        </article>
      `).join('');
    }

    function applyFilters() {
      const q = elements.searchInput.value.trim().toLowerCase();
      let items = [...allItems];

      if (activeCategory !== 'Tổng hợp') {
        items = items.filter(item => inferCategory(item) === activeCategory);
      }

      if (q) {
        items = items.filter(item => {
          const text = `${item.title || ''} ${item.snippet || ''} ${item.source || ''}`.toLowerCase();
          return text.includes(q);
        });
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

    async function loadData(isAutoRefresh = false) {
      const limit = Number(elements.limitInput.value) || 10;
      elements.apiStatus.textContent = isAutoRefresh ? 'Tự động cập nhật' : 'Đang tải';
      elements.statusText.textContent = isAutoRefresh ? 'Đang tự động cập nhật dữ liệu...' : 'Đang đồng bộ dữ liệu...';
      elements.summaryText.textContent = 'Đang tạo tóm tắt...';
      try {
        const [newsRes, summaryRes] = await Promise.all([
          fetch(`${API_BASE}/news?limit=${limit}`),
          fetch(`${API_BASE}/summarize?limit=${limit}`)
        ]);

        if (!newsRes.ok || !summaryRes.ok) throw new Error('API lỗi');

        const newsData = await newsRes.json();
        const summaryData = await summaryRes.json();

        allItems = Array.isArray(newsData.items) ? newsData.items : [];
        updateHero(newsData, summaryData);
        applyFilters();
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

    elements.searchInput.addEventListener('input', applyFilters);
    elements.limitInput.addEventListener('change', loadData);
    elements.reloadBtn.addEventListener('click', loadData);

    renderCategories();
    renderWatchlist();
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
def news(limit: int = Query(default=10, ge=1, le=50)):
    items = enrich_news_with_ai(collect_news(limit=limit))
    return {"total_items": len(items), "items": items}


@app.get("/summarize", response_model=SummarizeResponse)
def summarize(limit: int = Query(default=10, ge=1, le=50), max_chars: int = Query(default=1200, ge=300, le=4000)):
    items = enrich_news_with_ai(collect_news(limit=limit))
    summary = summarize_news(items, max_chars=max_chars)
    return {"total_items": len(items), "summary": summary, "items": items}

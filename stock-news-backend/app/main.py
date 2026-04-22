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
  <title>Stock News Dashboard</title>
  <style>
    :root {
      --bg: #0b1020;
      --panel: #121a2b;
      --panel-2: #182338;
      --text: #e8ecf3;
      --muted: #9fb0cc;
      --line: #26324a;
      --accent: #6ea8fe;
      --accent-2: #7ef0c8;
      --danger: #ff7a7a;
      --shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
      background: linear-gradient(180deg, #0a0f1d 0%, #0d1324 100%);
      color: var(--text);
    }
    .app {
      display: grid;
      grid-template-columns: 280px 1fr;
      min-height: 100vh;
    }
    .sidebar {
      border-right: 1px solid var(--line);
      background: rgba(9, 14, 28, 0.9);
      padding: 24px 18px;
      position: sticky;
      top: 0;
      height: 100vh;
    }
    .brand {
      font-size: 22px;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .sub {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
      margin-bottom: 24px;
    }
    .side-card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: var(--shadow);
    }
    .side-title {
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: var(--muted);
      margin-bottom: 10px;
    }
    .stat {
      font-size: 26px;
      font-weight: 700;
      margin-bottom: 6px;
    }
    .summary {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.6;
      white-space: pre-wrap;
    }
    .main {
      padding: 24px;
    }
    .topbar {
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }
    .search-wrap {
      flex: 1;
      min-width: 260px;
      display: flex;
      gap: 10px;
    }
    .search, .limit, .btn {
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--text);
      border-radius: 14px;
      padding: 12px 14px;
      font-size: 14px;
    }
    .search { flex: 1; }
    .limit { width: 88px; }
    .btn {
      background: linear-gradient(135deg, var(--accent), #8d7dff);
      border: none;
      color: white;
      cursor: pointer;
      font-weight: 600;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }
    .card {
      background: linear-gradient(180deg, rgba(24, 35, 56, 0.95), rgba(16, 24, 40, 0.95));
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .meta {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      font-size: 12px;
      color: var(--muted);
      flex-wrap: wrap;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(126, 240, 200, 0.12);
      color: var(--accent-2);
      border: 1px solid rgba(126, 240, 200, 0.18);
      padding: 6px 10px;
      border-radius: 999px;
      font-weight: 600;
      text-transform: capitalize;
    }
    .title {
      font-size: 18px;
      font-weight: 700;
      line-height: 1.45;
      margin: 0;
    }
    .snippet {
      color: #c6d1e6;
      line-height: 1.6;
      font-size: 14px;
      margin: 0;
      flex: 1;
    }
    .link {
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
    }
    .status {
      color: var(--muted);
      font-size: 14px;
      margin-bottom: 14px;
    }
    .error { color: var(--danger); }
    @media (max-width: 900px) {
      .app { grid-template-columns: 1fr; }
      .sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--line); }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">Stock News</div>
      <div class="sub">Dashboard tin tức chứng khoán từ backend FastAPI.</div>

      <div class="side-card">
        <div class="side-title">Tổng số tin</div>
        <div class="stat" id="totalCount">0</div>
        <div class="summary">Dữ liệu lấy trực tiếp từ <b>/news</b> và phần tóm tắt lấy từ <b>/summarize</b>.</div>
      </div>

      <div class="side-card">
        <div class="side-title">Tóm tắt nhanh</div>
        <div class="summary" id="summaryText">Đang tải...</div>
      </div>
    </aside>

    <main class="main">
      <div class="topbar">
        <div class="search-wrap">
          <input id="searchInput" class="search" type="text" placeholder="Tìm theo tiêu đề hoặc nguồn..." />
          <input id="limitInput" class="limit" type="number" min="1" max="20" value="10" />
          <button id="reloadBtn" class="btn">Làm mới</button>
        </div>
      </div>

      <div id="status" class="status">Đang tải dữ liệu...</div>
      <section id="newsGrid" class="grid"></section>
    </main>
  </div>

  <script>
    const API_BASE = '';
    const elements = {
      grid: document.getElementById('newsGrid'),
      status: document.getElementById('status'),
      total: document.getElementById('totalCount'),
      summary: document.getElementById('summaryText'),
      search: document.getElementById('searchInput'),
      limit: document.getElementById('limitInput'),
      reload: document.getElementById('reloadBtn')
    };

    let allItems = [];

    function escapeHtml(text = '') {
      return text
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
    }

    function formatTime(value) {
      if (!value) return 'Không rõ thời gian';
      return value;
    }

    function render(items) {
      elements.total.textContent = items.length;
      if (!items.length) {
        elements.grid.innerHTML = '';
        elements.status.textContent = 'Không có tin phù hợp.';
        return;
      }

      elements.status.textContent = `Hiển thị ${items.length} tin`;
      elements.grid.innerHTML = items.map(item => `
        <article class="card">
          <div class="meta">
            <span class="badge">${escapeHtml(item.source || 'unknown')}</span>
            <span>${escapeHtml(formatTime(item.published_at || item.fetched_at))}</span>
          </div>
          <h3 class="title">${escapeHtml(item.title || 'Không có tiêu đề')}</h3>
          <p class="snippet">${escapeHtml(item.snippet || 'Chưa có mô tả ngắn.')}</p>
          <a class="link" href="${escapeHtml(item.url || '#')}" target="_blank" rel="noreferrer">Xem bài gốc</a>
        </article>
      `).join('');
    }

    function applyFilter() {
      const q = elements.search.value.trim().toLowerCase();
      if (!q) return render(allItems);
      const filtered = allItems.filter(item => {
        const title = (item.title || '').toLowerCase();
        const source = (item.source || '').toLowerCase();
        const snippet = (item.snippet || '').toLowerCase();
        return title.includes(q) || source.includes(q) || snippet.includes(q);
      });
      render(filtered);
    }

    async function loadData() {
      const limit = Math.min(20, Math.max(1, Number(elements.limit.value) || 10));
      elements.status.textContent = 'Đang tải dữ liệu...';
      elements.summary.textContent = 'Đang tạo tóm tắt...';
      try {
        const [newsRes, summaryRes] = await Promise.all([
          fetch(`${API_BASE}/news?limit=${limit}`),
          fetch(`${API_BASE}/summarize?limit=${limit}`)
        ]);

        if (!newsRes.ok) throw new Error('Không tải được /news');
        if (!summaryRes.ok) throw new Error('Không tải được /summarize');

        const newsData = await newsRes.json();
        const summaryData = await summaryRes.json();

        allItems = Array.isArray(newsData.items) ? newsData.items : [];
        elements.summary.textContent = summaryData.summary || 'Chưa có tóm tắt.';
        applyFilter();
      } catch (error) {
        elements.grid.innerHTML = '';
        elements.summary.textContent = 'Không tải được dữ liệu.';
        elements.status.innerHTML = '<span class="error">Lỗi tải dữ liệu từ API.</span>';
      }
    }

    elements.search.addEventListener('input', applyFilter);
    elements.reload.addEventListener('click', loadData);
    elements.limit.addEventListener('change', loadData);

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

<?php

declare(strict_types=1);
require_once __DIR__ . '/../src/config.php';
?><!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars(APP_NAME, ENT_QUOTES, 'UTF-8') ?> - Dashboard</title>
    <style>
        :root {
            --bg: #0b1020;
            --card: #131a2e;
            --text: #ecf1ff;
            --muted: #9db0de;
            --positive: #16c47f;
            --negative: #ff5d73;
            --neutral: #f6c85f;
            --border: #243055;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Inter, Segoe UI, Roboto, sans-serif;
            background: linear-gradient(180deg, #0a0f1d 0%, #0b1020 100%);
            color: var(--text);
        }
        .container {
            max-width: 1160px;
            margin: 0 auto;
            padding: 24px;
        }
        h1 { margin: 0 0 8px; font-size: 28px; }
        .subtitle { color: var(--muted); margin-bottom: 20px; }
        .status {
            display: inline-flex;
            gap: 10px;
            padding: 8px 12px;
            background: #0f1730;
            border: 1px solid var(--border);
            border-radius: 999px;
            font-size: 13px;
            color: var(--muted);
        }
        .grid {
            margin-top: 20px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            min-height: 350px;
        }
        .card h2 { margin: 0 0 10px; font-size: 20px; }
        .headline { margin-bottom: 8px; color: #dbe5ff; }
        .sentiment {
            display: inline-block;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            margin-bottom: 12px;
        }
        .sentiment.positive { color: #062e1f; background: var(--positive); }
        .sentiment.negative { color: #400711; background: var(--negative); }
        .sentiment.neutral { color: #413207; background: var(--neutral); }
        ul { margin: 0; padding-left: 18px; }
        li { margin-bottom: 10px; }
        a { color: #a9c7ff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .footer {
            margin-top: 18px;
            color: var(--muted);
            font-size: 12px;
        }
        .loading {
            color: var(--muted);
            font-style: italic;
        }
        @media (max-width: 980px) {
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
<div class="container">
    <h1><?= htmlspecialchars(APP_NAME, ENT_QUOTES, 'UTF-8') ?></h1>
    <div class="subtitle">Dashboard tổng hợp tin real-time & tóm tắt nhanh: Chứng khoán • Kinh tế • BĐS</div>
    <div class="status">
        <span id="lastUpdated">Đang tải dữ liệu...</span>
        <span>•</span>
        <span>Tự động cập nhật mỗi 60 giây</span>
    </div>

    <div class="grid" id="cards">
        <div class="card" data-cat="stocks">
            <h2>📈 Chứng khoán</h2>
            <div class="loading">Đang lấy dữ liệu...</div>
        </div>
        <div class="card" data-cat="economy">
            <h2>🏛️ Kinh tế</h2>
            <div class="loading">Đang lấy dữ liệu...</div>
        </div>
        <div class="card" data-cat="real_estate">
            <h2>🏘️ Bất động sản</h2>
            <div class="loading">Đang lấy dữ liệu...</div>
        </div>
    </div>

    <div class="footer">
        Domain triển khai: <strong><?= htmlspecialchars(PRIMARY_DOMAIN, ENT_QUOTES, 'UTF-8') ?></strong><br>
        Dữ liệu từ RSS công khai. Nội dung tóm tắt chỉ để tham khảo, không phải khuyến nghị đầu tư.
    </div>
</div>

<script>
    const labels = {
        positive: 'Tích cực',
        negative: 'Thận trọng',
        neutral: 'Trung tính'
    };

    function fmtTime(iso) {
        try {
            return new Date(iso).toLocaleString('vi-VN');
        } catch (_) {
            return iso;
        }
    }

    function renderCard(cat, block, data) {
        const summary = data.summaries?.[cat] || { headline: 'Chưa có dữ liệu', sentiment: 'neutral', key_points: [] };
        const items = data.news?.[cat] || [];

        const sentimentClass = summary.sentiment || 'neutral';
        const sentimentText = labels[sentimentClass] || 'Trung tính';

        const pointsHtml = (summary.key_points || [])
            .map(p => `<li>${p}</li>`)
            .join('');

        const newsHtml = items.slice(0, 6).map(it => {
            const title = it.title || 'Không có tiêu đề';
            const link = it.link || '#';
            const src = it.source || 'unknown';
            const t = it.published_at ? fmtTime(it.published_at) : '';
            return `<li><a href="${link}" target="_blank" rel="noopener noreferrer">${title}</a><br><small style="color:#8ea1cf">${src} • ${t}</small></li>`;
        }).join('');

        block.innerHTML = `
            <h2>${block.querySelector('h2')?.textContent || ''}</h2>
            <div class="headline">${summary.headline || 'Chưa có dữ liệu.'}</div>
            <div class="sentiment ${sentimentClass}">${sentimentText}</div>
            <strong>Ý chính:</strong>
            <ul>${pointsHtml || '<li>Chưa có điểm nhấn.</li>'}</ul>
            <hr style="border-color:#25335d; opacity:.4; margin:14px 0">
            <strong>Tin mới:</strong>
            <ul>${newsHtml || '<li>Chưa có tin.</li>'}</ul>
        `;
    }

    async function loadData() {
        try {
            const res = await fetch('api.php?limit=12', { cache: 'no-store' });
            const data = await res.json();

            if (!data || data.ok !== true) throw new Error('API invalid');

            document.getElementById('lastUpdated').textContent = `Cập nhật: ${fmtTime(data.generated_at || new Date().toISOString())}`;

            document.querySelectorAll('.card').forEach(card => {
                renderCard(card.dataset.cat, card, data);
            });
        } catch (err) {
            document.getElementById('lastUpdated').textContent = 'Lỗi tải dữ liệu. Sẽ thử lại...';
            console.error(err);
        }
    }

    loadData();
    setInterval(loadData, 60000);
</script>
</body>
</html>

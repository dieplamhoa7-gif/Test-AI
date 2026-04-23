# VN Stock News Backend (CafeF + Vietstock)

Backend mẫu dùng FastAPI để:
1. Crawl/tổng hợp tin từ CafeF + Vietstock (ưu tiên RSS, fallback HTML)
2. Gọi AI để tóm tắt tin

## 1) Cài đặt

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Mở `.env` và điền:
- `OPENAI_API_KEY=...`
- `OPENAI_MODEL=gpt-4o-mini` (hoặc model bạn muốn)

## 2) Chạy server

```bash
uvicorn app.main:app --reload --port 8000
```

## Deploy

### Render
- Repo đã có `render.yaml`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Thiết lập env vars trên Render: `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL`

### Netlify
- Repo có `netlify.toml`
- Hiện dự án này là FastAPI fullstack render từ backend, nên Render là nơi phù hợp để chạy chính.
- Netlify chỉ nên dùng nếu sau này tách frontend tĩnh riêng.

## 3) API

- `GET /health`
- `GET /news?limit=10`
- `GET /summarize?limit=10&max_chars=1200`
- `GET /market-data` → trả về mảng object cho React/Next.js map()

## 4) Lưu ý pháp lý/kỹ thuật khi crawl

- Nên ưu tiên RSS/API chính thức để giảm rủi ro bị chặn.
- Tôn trọng robots.txt, điều khoản sử dụng, và rate limit.
- Nếu source đổi giao diện, cần cập nhật selector HTML.
- Không dùng dữ liệu tóm tắt AI làm khuyến nghị đầu tư trực tiếp.

## 5) Gợi ý production

- Thêm scheduler (Celery/APScheduler) để crawl định kỳ.
- Lưu DB (Postgres) + cache (Redis).
- Track duplicate bằng hash URL + title.
- Add auth, logging, metrics, alerting.


### MongoDB
- Env vars hỗ trợ: MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION
- Nếu có MONGODB_URI, app sẽ lưu tối đa 100 tin trên MongoDB thay vì file local.

### Market Data
- `GET /market-data` trả về array object gồm ticker, price, changePct, volume, chart, technical.
- Có nền cập nhật dữ liệu mỗi 30 giây khi app chạy.
- Đã bật CORS cho localhost:3000 / 5173.
- Đã thêm `vnstock3` vào requirements cho bước tích hợp nguồn thực tế.

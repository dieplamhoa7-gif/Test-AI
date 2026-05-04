from app.services.scraper import collect_news
from app.services.summarizer import enrich_news_with_ai
from app.store import merge_news


def main():
    raw = collect_news(limit=150)
    print('raw', len(raw), flush=True)
    if raw:
        try:
            fresh = enrich_news_with_ai(raw)
        except Exception as exc:
            print('enrich failed', exc, flush=True)
            fresh = raw
        saved = merge_news(fresh)
    else:
        saved = []
    saved = saved[:500]
    print('saved', len(saved), flush=True)
    if saved:
        print(saved[0].get('published_at'), saved[0].get('title'), flush=True)


if __name__ == '__main__':
    main()

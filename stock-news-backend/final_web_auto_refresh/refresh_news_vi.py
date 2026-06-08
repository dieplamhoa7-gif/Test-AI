from app.services.scraper import collect_news
from app.store import merge_news


def main():
    raw = collect_news(limit=150)
    print('raw', len(raw), flush=True)
    # Keep auto-refresh reliable: do not block news publishing on slow AI/enrich.
    # Translation/report steps run after this; raw fresh news is better than a stuck pipeline.
    if raw:
        saved = merge_news(raw)
    else:
        saved = []
    saved = saved[:500]
    print('saved', len(saved), flush=True)
    if saved:
        title = str(saved[0].get('title') or '').encode('ascii', 'backslashreplace').decode('ascii')
        print(saved[0].get('published_at'), title, flush=True)


if __name__ == '__main__':
    main()

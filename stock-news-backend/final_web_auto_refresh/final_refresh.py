from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = Path(__file__).resolve().parent
REPORT_DIR = ROOT / 'data' / 'final_auto_refresh_reports'
TZ = timezone(timedelta(hours=7))


def run(cmd: list[str], timeout: int = 1800) -> dict:
    print('[final-refresh] RUN', ' '.join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout, encoding='utf-8', errors='replace')
    stdout = p.stdout or ''
    stderr = p.stderr or ''
    out = {
        'cmd': cmd,
        'returncode': p.returncode,
        'stdoutTail': stdout[-8000:],
        'stderrTail': stderr[-8000:],
    }
    if stdout:
        print(stdout[-4000:], flush=True)
    if stderr:
        print(stderr[-4000:], file=sys.stderr, flush=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed {p.returncode}: {' '.join(cmd)}\n{p.stderr[-2000:]}")
    return out


def py(script: str, *args: str, timeout: int = 1800) -> dict:
    return run([sys.executable, script, *args], timeout=timeout)


def latest_chart_date(symbol='MWG') -> str | None:
    p = ROOT / 'firebase_public' / 'data' / 'charts' / f'{symbol}.json'
    if not p.exists(): return None
    try:
        j=json.loads(p.read_text(encoding='utf-8'))
        rows=j.get('rows') or []
        return rows[-1].get('time') if rows else None
    except Exception:
        return None


def write_report(mode: str, steps: list[dict]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        'mode': mode,
        'createdAt': datetime.now(TZ).isoformat(timespec='seconds'),
        'chartMWGLastDate': latest_chart_date('MWG'),
        'steps': steps,
    }
    (REPORT_DIR / f'{mode}_latest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    pub = ROOT / 'firebase_public' / 'data' / 'final_auto_refresh_reports'
    pub.mkdir(parents=True, exist_ok=True)
    (pub / f'{mode}_latest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'mode': mode, 'chartMWGLastDate': report['chartMWGLastDate'], 'steps': len(steps)}, ensure_ascii=False), flush=True)


def mode_intraday() -> list[dict]:
    steps=[]
    # Daily OHLC chart cache. This is intentionally separate from price ticker cache.
    steps.append(py('refresh_vn100_history_for_core12.py', timeout=2400))
    steps.append(py('build_stock_chart_cache.py', timeout=600))
    # touchzone is optional in some branches; run if present.
    if (ROOT/'export_touchzone_all_day.py').exists():
        steps.append(py('export_touchzone_all_day.py', timeout=900))
    steps.append(py('build_firebase_cache_site.py', timeout=600))
    return steps


def mode_eod() -> list[dict]:
    steps=[]
    steps.append(py('refresh_eod_all_stocks_lh.py', timeout=1800))
    steps.append(py('refresh_vn100_history_for_core12.py', timeout=2400))
    steps.append(py('build_stock_chart_cache.py', timeout=600))
    if (ROOT/'export_touchzone_all_day.py').exists():
        steps.append(py('export_touchzone_all_day.py', timeout=900))
    steps.append(py('refresh_warrants_cache_lh.py', timeout=900))
    steps.append(py('build_firebase_cache_site.py', timeout=600))
    return steps


def mode_warrants() -> list[dict]:
    return [py('refresh_warrants_cache_lh.py', timeout=900), py('build_firebase_cache_site.py', timeout=600)]


def mode_news() -> list[dict]:
    steps=[]
    steps.append(py('refresh_news_cache_lh.py', timeout=900))
    steps.append(py('build_news_translate_cache.py', '--limit', '120', timeout=1200))
    steps.append(py('build_firebase_cache_site.py', timeout=600))
    return steps


def main():
    ap=argparse.ArgumentParser(description='FINAL LH Investment web auto-refresh runner')
    ap.add_argument('--mode', choices=['intraday','eod','warrants','news','all'], required=True)
    args=ap.parse_args()
    all_steps=[]
    if args.mode in ['intraday','all']:
        all_steps += mode_intraday()
    if args.mode in ['eod','all']:
        all_steps += mode_eod()
    if args.mode in ['warrants','all']:
        all_steps += mode_warrants()
    if args.mode in ['news','all']:
        all_steps += mode_news()
    write_report(args.mode, all_steps)

if __name__ == '__main__':
    main()

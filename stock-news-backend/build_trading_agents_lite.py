from __future__ import annotations

"""Deterministic TradingAgents-lite layer for LH Investment.

Security model:
- Does NOT import or execute TauricResearch/TradingAgents or any third-party repo code.
- Does NOT run shell commands.
- Does NOT call network APIs or LLM providers.
- Reads only local cache JSON files produced by the LH pipeline.
- Produces local JSON explainability/decision-log style output for the web.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = DATA / "trading_agents_lite.json"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def num(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", ""))
    except Exception:
        return default


def as_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        items = payload.get("items")
        return [x for x in items if isinstance(x, dict)] if isinstance(items, list) else []
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    return []


def flatten_strategy_items(strategy_payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for strat in strategy_payload.get("strategies", []) if isinstance(strategy_payload, dict) else []:
        if not isinstance(strat, dict):
            continue
        sid = str(strat.get("id") or "strategy")
        for bucket in ["buy", "watchlist", "items"]:
            rows = strat.get(bucket) or []
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                sym = str(row.get("symbol") or row.get("ticker") or "").upper().strip()
                if not sym:
                    continue
                x = dict(row)
                x.setdefault("strategyId", sid)
                x.setdefault("action", "BUY" if bucket == "buy" else "WATCH")
                out.setdefault(sym, []).append(x)
    return out


def make_market_map() -> dict[str, dict[str, Any]]:
    rows = as_items(read_json(DATA / "market_data.json", {"items": []}))
    return {str(x.get("symbol") or x.get("ticker") or "").upper(): x for x in rows if str(x.get("symbol") or x.get("ticker") or "").strip()}


def make_core12_map() -> dict[str, dict[str, Any]]:
    rows = as_items(read_json(DATA / "core12_ml_sr_full_universe.json", {"items": []}))
    return {str(x.get("symbol") or x.get("ticker") or "").upper(): x for x in rows if str(x.get("symbol") or x.get("ticker") or "").strip()}


def technical_agent(sym: str, market: dict[str, Any], signals: list[dict[str, Any]]) -> dict[str, Any]:
    tech = market.get("technical") if isinstance(market.get("technical"), dict) else {}
    rsi = num(market.get("rsi14") or tech.get("rsi14"))
    adx = num(market.get("adx14") or tech.get("adx14"))
    change = num(market.get("changePct") or tech.get("changePct"), 0) or 0
    price = num(market.get("price") or tech.get("price"))
    score = 50.0
    reasons: list[str] = []
    if signals:
        score += min(25, len(signals) * 8)
        reasons.append(f"Có {len(signals)} tín hiệu chiến lược")
    if rsi is not None:
        if 45 <= rsi <= 65:
            score += 8; reasons.append(f"RSI cân bằng {rsi:.1f}")
        elif rsi > 75:
            score -= 10; reasons.append(f"RSI cao {rsi:.1f}, dễ rung/lắc")
        elif rsi < 35:
            score -= 6; reasons.append(f"RSI yếu {rsi:.1f}")
    if adx is not None and adx >= 20:
        score += 5; reasons.append(f"ADX {adx:.1f} có xu hướng")
    if change > 3:
        score -= 4; reasons.append("Giá tăng mạnh trong phiên, tránh đuổi")
    if not reasons:
        reasons.append("Chưa đủ tín hiệu kỹ thuật nổi bật")
    return {"score": round(max(0, min(100, score)), 1), "price": price, "reasons": reasons[:5]}


def bull_agent(signals: list[dict[str, Any]], core: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    score = 40.0
    for s in sorted(signals, key=lambda x: num(x.get("rankScore"), 0) or 0, reverse=True)[:3]:
        action = str(s.get("action") or "WATCH")
        sid = str(s.get("strategyId") or s.get("strategy") or "strategy")
        rank = num(s.get("rankScore"))
        if action.upper() == "BUY": score += 18
        else: score += 8
        reasons.append(f"{action} từ {sid}" + (f" rank {rank:.0f}" if rank is not None else ""))
    hold = num(core.get("holdScore"))
    pos = num(core.get("core12Positive"))
    if hold is not None and hold >= 60:
        score += 12; reasons.append(f"Core12 giữ hỗ trợ tốt holdScore {hold:.0f}")
    if pos is not None and pos >= 3:
        score += 8; reasons.append(f"Core12 tích cực {pos:.0f} nhóm")
    if not reasons:
        reasons.append("Case tăng chưa rõ, cần thêm xác nhận")
    return {"score": round(max(0, min(100, score)), 1), "reasons": reasons[:5]}


def bear_agent(market: dict[str, Any], signals: list[dict[str, Any]], core: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    score = 35.0
    risk = num(core.get("breakRiskScore"))
    neg = num(core.get("core12Negative"))
    status = str(core.get("finalStatus") or core.get("priceStatus") or "")
    volume = num(market.get("volume"))
    if risk is not None and risk >= 60:
        score += 25; reasons.append(f"Rủi ro gãy hỗ trợ cao {risk:.0f}")
    if neg is not None and neg >= 3:
        score += 12; reasons.append(f"Core12 tiêu cực {neg:.0f} nhóm")
    if "YẾU" in status.upper() or "YEU" in status.upper():
        score += 10; reasons.append(status)
    if any(num(s.get("distSupportPct"), 0) is not None and (num(s.get("distSupportPct"), 0) or 0) < -1 for s in signals):
        score += 6; reasons.append("Một số setup đã nằm dưới vùng hỗ trợ dự kiến")
    if volume is not None and volume < 100000:
        score += 8; reasons.append("Thanh khoản thấp")
    if not reasons:
        reasons.append("Chưa thấy rủi ro định lượng lớn")
    return {"score": round(max(0, min(100, score)), 1), "reasons": reasons[:5]}


def risk_manager(tech: dict[str, Any], bull: dict[str, Any], bear: dict[str, Any]) -> dict[str, Any]:
    buy_score = 0.45 * tech["score"] + 0.40 * bull["score"] - 0.35 * bear["score"] + 25
    buy_score = round(max(0, min(100, buy_score)), 1)
    if bear["score"] >= 75:
        verdict = "REJECT_RISK"
    elif buy_score >= 68 and bear["score"] < 60:
        verdict = "BUY_CANDIDATE"
    elif buy_score >= 50:
        verdict = "WATCH"
    else:
        verdict = "REJECT"
    return {"verdict": verdict, "buyScore": buy_score, "riskScore": bear["score"]}


def build() -> dict[str, Any]:
    market_map = make_market_map()
    core_map = make_core12_map()
    strategy_payload = read_json(DATA / "strategy_results_cache.json", {})
    signal_map = flatten_strategy_items(strategy_payload if isinstance(strategy_payload, dict) else {})
    symbols = sorted(set(market_map) | set(core_map) | set(signal_map))
    items: list[dict[str, Any]] = []
    for sym in symbols:
        market = market_map.get(sym, {})
        core = core_map.get(sym, {})
        signals = signal_map.get(sym, [])
        tech = technical_agent(sym, market, signals)
        if not tech.get("price"):
            tech["price"] = num(core.get("close"))
        bull = bull_agent(signals, core)
        bear = bear_agent(market, signals, core)
        decision = risk_manager(tech, bull, bear)
        items.append({
            "symbol": sym,
            "asOf": core.get("date") or (signals[0].get("asOfDate") if signals else None),
            "price": tech.get("price") or core.get("close"),
            "decision": decision,
            "agents": {"technical": tech, "bull": bull, "bear": bear},
            "topReasons": (bull["reasons"][:2] + bear["reasons"][:2])[:4],
            "securityNote": "Local deterministic agent-lite; no external repo code, no shell, no network, no LLM call.",
        })
    items.sort(key=lambda x: (x["decision"]["verdict"] not in {"BUY_CANDIDATE", "WATCH"}, -x["decision"]["buyScore"], x["symbol"]))
    return {
        "updatedAt": datetime.now().isoformat(timespec="seconds"),
        "source": "LH TradingAgents-lite deterministic local cache",
        "security": {
            "thirdPartyRepoImported": False,
            "networkCalls": False,
            "shellExecution": False,
            "llmCalls": False,
            "reads": ["market_data.json", "core12_ml_sr_full_universe.json", "strategy_results_cache.json"],
        },
        "count": len(items),
        "items": items,
    }


def main() -> None:
    payload = build()
    write_json(OUT, payload)
    print(json.dumps({"output": str(OUT), "count": payload["count"], "top": payload["items"][:5]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

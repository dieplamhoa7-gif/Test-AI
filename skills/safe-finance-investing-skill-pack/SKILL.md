# Safe Finance Investing Skill Pack

## Purpose

Use this skill when Hòa Đại ka asks for:

- stock/market technical analysis,
- chart image analysis,
- fundamental/financial report analysis,
- quantitative stock screening,
- professional PDF/report generation,
- frontend/UI polish for finance dashboards.

This is a **clean internal rewrite** inspired by public ClawHub skill categories that Hòa Đại ka selected. It intentionally does **not** copy external code and does **not** execute third-party scripts.

## Safety Rules

1. Do not install or run external ClawHub/GitHub code unless separately vetted.
2. Do not send files, API keys, tokens, or financial data to unknown endpoints.
3. Do not use network calls unless the task explicitly requires data fetching and the source is known.
4. Prefer local files and existing workspace data.
5. For production LH Investment/Firebase work, obey `skills/lh-investment-firebase-final-deploy/SKILL.md`.
6. For strategy/model work, obey no-lookahead and OOS discipline.

## Source Ideas Rewritten Internally

This skill rewrites the ideas of these public skill categories without importing code:

- TradingView quantitative / technical pattern analysis.
- Chart image technical analyst.
- Finance report analyzer from PDF/Excel.
- Professional PDF generator.
- Frontend design polish/audit.

## Module A — Quantitative / Technical Stock Analysis

Use when asked to analyze stocks technically or screen candidates.

### Required Output Structure

```json
{
  "symbol": "MWG",
  "timeframe": "daily/weekly/monthly",
  "trend": {},
  "momentum": {},
  "volume": {},
  "volatility": {},
  "supportResistance": {},
  "patterns": [],
  "riskReward": {},
  "scenario": {
    "bullCase": "",
    "baseCase": "",
    "bearCase": ""
  },
  "invalidIf": "",
  "confidence": "low/medium/high",
  "dataLimitations": []
}
```

### Technical Checklist

- Trend: MA20/50/200, slope, price-vs-MA, higher highs/lows.
- Momentum: RSI, MACD histogram, ROC, divergence if reliable.
- Volume: volume ratio, accumulation/distribution clues, breakout confirmation.
- Volatility: ATR%, realized volatility, Bollinger width.
- Support/resistance: nearest support, nearest resistance, distance to each.
- Pattern: only as confluence; do not treat as standalone signal.
- Risk/reward: stop, target, invalidation, room-to-resistance.

### Discipline

- Avoid certainty language.
- Separate observation from recommendation.
- Always state timeframe.
- If using historical performance, require no-lookahead backtest.

## Module B — Chart Image Analyst

Use when Hòa Đại ka sends chart screenshots.

### Workflow

1. Identify chart metadata visible in image:
   - symbol,
   - timeframe,
   - date range,
   - indicators shown.
2. Read structure:
   - trend direction,
   - support/resistance zones,
   - volume behavior,
   - breakout/breakdown/retest,
   - volatility compression/expansion.
3. Give scenarios:
   - bullish continuation,
   - base/sideway,
   - bearish failure.
4. State invalidation.
5. State what additional data is needed.

### Output Template

```text
Quan sát chart:
- ...

Vùng giá quan trọng:
- Hỗ trợ: ...
- Kháng cự: ...

Kịch bản:
1. Bull case: ...
2. Base case: ...
3. Bear case: ...

Sai nếu:
- ...

Cần thêm:
- volume/date/timeframe/market context...
```

## Module C — Fundamental / Financial Report Analyzer

Use when analyzing annual reports, financial statements, Excel models, PDFs, or valuation reports.

### Required Analysis Sections

1. Business model and revenue drivers.
2. Revenue, gross margin, operating margin, net margin trend.
3. Balance sheet quality:
   - debt,
   - cash,
   - working capital,
   - receivables/inventory.
4. Cash flow quality:
   - CFO vs net profit,
   - capex,
   - free cash flow.
5. Valuation:
   - P/E,
   - P/B,
   - EV/EBITDA,
   - DCF if suitable.
6. Risk factors:
   - leverage,
   - cyclicality,
   - governance,
   - macro/rates,
   - FX/commodity exposure.
7. Investment view:
   - bull/base/bear case,
   - key assumptions,
   - what would change the view.

### Rules

- Separate reported numbers from assumptions.
- If numbers are extracted from OCR/PDF, mark confidence.
- Never invent missing financial figures.
- For DCF, show WACC, terminal growth, and sensitivity.

## Module D — Professional PDF / Report Generator

Use when creating PDF reports, study guides, investment memos, or slide decks.

### Report Quality Standards

- Strong cover page.
- Clear table of contents.
- Page numbers and footer.
- Consistent color palette.
- Section banners.
- Tables for comparisons.
- Formula boxes.
- Investment application boxes.
- Key takeaway boxes.
- No half-empty pages unless intentional slide design.

### Recommended Structure

```text
1. Cover
2. Table of contents
3. Executive summary
4. Main modules/chapters
5. Formula summary
6. Practical checklist
7. References / data limitations
```

### Style Palette

- Navy: `#1B2B4B` for headers.
- MIT red: `#A31F34` for accent.
- Blue: `#2E5FA3` for section headings.
- Gold: `#C49A1B` for takeaways.
- Green: `#1B5E20` for investment boxes.
- Light gray: `#F4F6FA` for formula backgrounds.

### Tooling Preference

- For slide-like PDFs: HTML/CSS + Playwright Chromium.
- For dense documents: ReportLab or HTML/CSS with paged layout.
- For markdown source: always create `.md` alongside `.pdf`.

## Module E — Frontend / UI Polish for Finance Dashboards

Use when polishing LH Investment or finance dashboards.

### Audit Checklist

- Information hierarchy:
  - what should user see first?
  - are signals/risk clearly separated?
- Data density:
  - dense enough for finance users,
  - not cluttered.
- Visual encoding:
  - green/red used consistently,
  - avoid decorative colors with no meaning.
- Tables:
  - sortable, scannable, aligned numbers,
  - fixed important columns if needed.
- Cards:
  - show metric, delta, timeframe, confidence.
- Risk display:
  - invalidation, stop, downside, regime.
- Mobile/responsive layout.

### Avoid

- Generic AI gradients everywhere.
- Huge whitespace that reduces information value.
- Redesigning production UI without approval.
- Rebuilding Firebase static HTML from old templates.

## Module F — Selection Recommendations from ClawHub Search

The following public skills were considered useful by category, but should not be installed blindly:

### Finance / market data

- `@anton-roos / finance` — general market quotes/tracking.
- `@qiujiahong / Finance Report Analyzer` — financial data from Excel/PDF and report output.
- `@hj2916 / financial-report-analyzer` — PDF financial report extraction.

### Technical / stock analysis

- `@hypier / Tradingview Quantitative` — quantitative/TradingView-style screening and pattern recognition.
- `@veeramanikandanr48 / Technical Analyst` — chart image technical analysis.
- `@veeramanikandanr48 / Us Stock Analysis` — combined fundamental and technical report structure.
- `@yumyumtum / yumstock` — macro-gated stock scoring.

### PDF/report

- `@ivangdavila / Pdf Generator` — general professional PDF generation.
- `@0xvespertine / PDF Report` — JSON/Jinja2/WeasyPrint report idea.
- `@smseow001 / MiniMax PDF` — Playwright + ReportLab dual-engine idea.

### Design/frontend

- `@michaelmonetized / Frontend Design` — high-quality frontend interfaces.
- `@antonia-sz / Frontend Design Pro` — audit/polish/critique design workflow.
- `@ivangdavila / Design` — learn visual preferences.

## Default Behavior

When asked to use this skill:

1. Clarify the asset/document/output type if unclear.
2. Use the corresponding module.
3. Produce structured output.
4. Include assumptions and limitations.
5. For files/PDF/UI, save source files and commit.

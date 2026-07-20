from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from vietnamese_text_guard import repair_vietnamese_text, vietnamese_quality_report

WORKSPACE = Path(r"C:\Users\HoaD-CVDT\.openclaw\workspace")
TEMP_DIR = WORKSPACE / "temp" / "notebooklm-share"
PROFILE_STATE = TEMP_DIR / "nlm-profile-pool-state.json"
NLM = Path(os.environ.get("NLM_EXE", Path(os.environ.get("LOCALAPPDATA", "")) / r"Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts\nlm.exe"))

NOTEBOOKLM_STOCK_PROMPT = """
Báº¡n lÃ  chuyÃªn gia phÃ¢n tÃ­ch Ä‘áº§u tÆ° chá»©ng khoÃ¡n, TradingAgents research coordinator vÃ  chuyÃªn gia thiáº¿t káº¿ báº£n trÃ¬nh bÃ y tÃ i chÃ­nh cho lÃ£nh Ä‘áº¡o/quá»¹ Ä‘áº§u tÆ°.

NHIá»†M Vá»¤: Äá»c TOÃ€N Bá»˜ file bÃ¡o cÃ¡o cá»• phiáº¿u Ä‘Ã£ upload vÃ  táº¡o Báº¢N TRÃŒNH BÃ€Y Dá»ŒC / PORTRAIT tá»« ná»™i dung bÃ¡o cÃ¡o.

YÃŠU Cáº¦U QUAN TRá»ŒNG NHáº¤T:
1. PHáº¢I GIá»® NGUYÃŠN TOÃ€N Bá»˜ Ná»˜I DUNG QUAN TRá»ŒNG trong file bÃ¡o cÃ¡o.
2. ÄÆ°á»£c phÃ©p viáº¿t láº¡i cÃ¢u chá»¯ ngáº¯n gá»n hÆ¡n, sÃºc tÃ­ch hÆ¡n, nhÆ°ng KHÃ”NG Ä‘Æ°á»£c lÃ m máº¥t Ã½, máº¥t sá»‘ liá»‡u, máº¥t nguá»“n, máº¥t luáº­n Ä‘iá»ƒm, máº¥t cáº£nh bÃ¡o hoáº·c máº¥t Ä‘iá»u kiá»‡n theo dÃµi.
3. KhÃ´ng Ä‘Æ°á»£c bá» qua: tin tá»©c/nguá»“n, tÃ¡c Ä‘á»™ng tÃ­ch cá»±c-tiÃªu cá»±c-trung tÃ­nh, sentiment, market snapshot, chiáº¿n lÆ°á»£c LH, tá»«ng chá»‰ bÃ¡o RSI/MACD/volume/ROC/Ichimoku/Bollinger/MA/ADX/RS support-resistance, rankScore, entry/stop/takeprofit, fundamental/valuation, bull/bear, catalyst, invalidation, risk score, trade plan, data gaps vÃ  disclaimer.

NGUYÃŠN Táº®C EVIDENCE-ONLY:
- Chá»‰ sá»­ dá»¥ng thÃ´ng tin cÃ³ trong file bÃ¡o cÃ¡o.
- KhÃ´ng tá»± láº¥y thÃªm dá»¯ liá»‡u ngoÃ i. KhÃ´ng bá»‹a sá»‘ liá»‡u, khÃ´ng suy diá»…n ngoÃ i bÃ¡o cÃ¡o.
- Náº¿u thÃ´ng tin khÃ´ng cÃ³ trong bÃ¡o cÃ¡o, ghi: â€œKhÃ´ng cÃ³ trong bÃ¡o cÃ¡oâ€. Náº¿u dá»¯ liá»‡u cÅ©/chÆ°a xÃ¡c nháº­n, giá»¯ nguyÃªn cáº£nh bÃ¡o nhÆ° â€œCache chÆ°a xÃ¡c nháº­nâ€, â€œCáº§n cáº­p nháº­t EOD/volume má»›iâ€, â€œChÆ°a Ä‘á»§ cÆ¡ sá»Ÿ káº¿t luáº­nâ€.
- KhÃ´ng Ä‘Æ°a khuyáº¿n nghá»‹ Ä‘áº§u tÆ° cÃ¡ nhÃ¢n hÃ³a; chá»‰ trÃ¬nh bÃ y phÃ¢n tÃ­ch, ká»‹ch báº£n, Ä‘iá»u kiá»‡n theo dÃµi.

YÃŠU Cáº¦U Bá» Cá»¤C MODEL 3 / NOTEBOOKLM:
- Má»¥c tiÃªu chÃ­nh: táº¡o ÄÃšNG 2 TRANG Dá»ŒC DÃ€I / EXACTLY TWO long portrait pages, Ä‘á»™ phÃ¢n giáº£i cao, nhÃ¬n nhÆ° áº£nh máº«u dashboard/report dÃ i.
- KhÃ´ng táº¡o 1 trang, khÃ´ng táº¡o 3+ trang, khÃ´ng táº¡o slide deck ngang/thÆ°a. Báº¯t buá»™c chia thÃ nh Ä‘Ãºng 2 trang dá»c dense Ä‘á»ƒ Ä‘á»§ ná»™i dung hÆ¡n.
- Má»—i trang pháº£i lÃ  má»™t pháº§n cá»§a cÃ¹ng má»™t bÃ¡o cÃ¡o dÃ i liÃªn tá»¥c, khÃ´ng Ä‘Æ°á»£c thÃ nh slide thuyáº¿t trÃ¬nh rá»i ráº¡c.
- Trang 1 chá»©a panel 01â€“05; Trang 2 chá»©a panel 06â€“10. Má»—i trang dense, nhiá»u báº£ng/Ã´ nhá», Ã­t khoáº£ng tráº¯ng, nhiá»u visual/smartart.

PHONG CÃCH THIáº¾T Káº¾:
- Phong cÃ¡ch theo áº£nh máº«u: A4/portrait infographic dashboard siÃªu dense, ná»n xanh navy/blue-gradient, header lá»›n, nhiá»u panel nhá» viá»n sÃ¡ng, Ã­t khoáº£ng tráº¯ng.
- Dark-tech/institutional research dashboard: ná»n navy/xanh Ä‘áº­m (#071B3A, #0B2A5B, #123B7A), chá»¯ tráº¯ng/xanh nháº¡t, font sans-serif hiá»‡n Ä‘áº¡i.
- Pháº£i cÃ³ visual hooks thu hÃºt: hero visual/header graphic, icon nhá» cho tá»«ng panel, mini chart/sparkline, gauge/donut, heatmap, arrow flow, faint stock chart watermark hoáº·c grid/glow decoration náº¿u cÃ³ thá»ƒ.
- KhÃ´ng Ä‘Æ°á»£c bá» chá»‰ bÃ¡o ká»¹ thuáº­t Ä‘Ã£ cÃ³ trong DOCX; náº¿u nhiá»u chá»‰ bÃ¡o thÃ¬ Ä‘Æ°a vÃ o báº£ng/matrix nhá» thay vÃ¬ cáº¯t bá».
- KhÃ´ng Ä‘Æ°á»£c chá»‰ lÃ  báº£ng chá»¯ Ä‘Æ¡n Ä‘iá»‡u; má»—i trang cáº§n 3-5 yáº¿u tá»‘ visual ngoÃ i chá»¯/báº£ng.
- Æ¯u tiÃªn báº£n biá»ƒu/card nhá» gá»n thay vÃ¬ Ä‘oáº¡n vÄƒn dÃ i: KPI strip nhá», báº£ng chá»‰ bÃ¡o, timeline, matrix, badge, gauge, checklist.
- LÃ m thÃ´ng tin nhá» láº¡i: bullet ngáº¯n, cÃ¢u ngáº¯n, chá»¯ trong tá»«ng Ã´/card nhá» gá»n hÆ¡n, nhiá»u cá»™t/báº£ng hÆ¡n; má»—i trang nÃªn cÃ³ 8-14 block nhá» hoáº·c 3-5 báº£ng/matrix; nhÆ°ng tuyá»‡t Ä‘á»‘i khÃ´ng máº¥t ná»™i dung quan trá»ng.
- Accent cyan/vÃ ng/cam/Ä‘á»/xanh lÃ¡. NhÃ£n mÃ u: TÃ­ch cá»±c xanh/cyan; TiÃªu cá»±c Ä‘á»/cam; Trung tÃ­nh/chÆ°a rÃµ xÃ¡m/vÃ ng; Rá»§i ro Ä‘á»/cam.

Bá» Cá»¤C Báº®T BUá»˜C â€” 2 TRANG Dá»ŒC DÃ€I Gá»’M 10 Báº¢NG/Ã” NHá»Ž:
TRANG 1: panel 01â€“05. TRANG 2: panel 06â€“10. KhÃ´ng bá» panel nÃ o.
01. HEADER / HERO: mÃ£ cá»• phiáº¿u, tÃªn doanh nghiá»‡p, ngÃ y dá»¯ liá»‡u, tráº¡ng thÃ¡i dá»¯ liá»‡u, visual stock/market.
02. EXECUTIVE SUMMARY: 3â€“5 Ã½ chÃ­nh nháº¥t, verdict, sentiment, Ä‘iá»ƒm cáº§n theo dÃµi.
03. KPI SNAPSHOT: giÃ¡, % thay Ä‘á»•i, volume/thanh khoáº£n, rankScore, risk score, data freshness.
04. NEWS & CATALYST TIMELINE: tin tá»©c, nguá»“n, tÃ¡c Ä‘á»™ng tÃ­ch cá»±c/tiÃªu cá»±c/trung tÃ­nh.
05. MARKET / SECTOR CONTEXT: VNIndex/ngÃ nh/vÄ© mÃ´ náº¿u cÃ³ trong bÃ¡o cÃ¡o, tÃ¡c Ä‘á»™ng ngáº¯n gá»n.
06. TECHNICAL MATRIX: RSI, MACD, MA, ADX/DI, Bollinger, Ichimoku, ROC/ret5, volume, support/resistance/RS.
07. LH STRATEGY BOX: strategy status, entry, stop, take profit, invalidation, Ä‘iá»u kiá»‡n kÃ­ch hoáº¡t.
08. FUNDAMENTAL / VALUATION: KQKD, valuation, driver, target/mean/median náº¿u cÃ³.
09. BULL / BASE / BEAR + RISK: 3 ká»‹ch báº£n, catalyst, risk probability-impact, Ä‘iá»ƒm há»§y luáº­n Ä‘iá»ƒm.
10. ACTION CHECKLIST / DISCLAIMER: checklist theo dÃµi, dá»¯ liá»‡u thiáº¿u, cáº£nh bÃ¡o, disclaimer.

MAP Ná»˜I DUNG DOCX â†’ PANEL (báº¯t buá»™c láº¥y Ä‘Ãºng nguá»“n, khÃ´ng bá» sÃ³t):
- Má»¥c 1 + 1B (Quan Ä‘iá»ƒm tá»•ng há»£p + Äiá»ƒm tá»•ng há»£p 4 lá»›p) â†’ panel 02 Executive Summary + 03 KPI Snapshot: giá»¯ nguyÃªn verdict, Ä‘iá»ƒm tá»«ng lá»›p vÃ  báº±ng chá»©ng.
- Má»¥c 2 (báº£ng tin cÃ³ nhÃ£n sentiment) â†’ panel 04 News & Catalyst Timeline: giá»¯ nhÃ£n TÃ­ch cá»±c/TiÃªu cá»±c/Trung tÃ­nh vÃ  sá»‘ Ä‘áº¿m sentiment.
- Má»¥c 4A/4B (vÄ© mÃ´, tÃ¡c Ä‘á»™ng ngÃ nh) â†’ panel 05 Market/Sector Context.
- Má»¥c 3 + 3B + 3C (Indicator Matrix, 4 cáº·p chá»‰ bÃ¡o, tÃ­n hiá»‡u há»‡ thá»‘ng V3: xu hÆ°á»›ng hiá»‡u lá»±c, phÃ¢n ká»³ RSI/MACD, Ichimoku, VWAP, Fibonacci, Donchian, Risk/Reward, signal score) â†’ panel 06 Technical Matrix: KHÃ”NG Ä‘Æ°á»£c bá» báº¥t ká»³ tÃ­n hiá»‡u nÃ o cá»§a má»¥c 3C.
- Má»¥c 3D (LH Strategy Box: chiáº¿n lÆ°á»£c, tráº¡ng thÃ¡i, entry/stop/TP) â†’ panel 07 LH Strategy Box.
- Má»¥c 4C (P/E, target CTCK, upside, stop loss CTCK, bÃ¡o cÃ¡o CTCK má»›i nháº¥t) â†’ panel 08 Fundamental/Valuation.
- Má»¥c 5 + 6 (ká»‹ch báº£n Bull/Base/Bear gáº¯n sá»‘ liá»‡u, catalyst) + má»¥c 7 (risk score X/5 kÃ¨m cÃ¡c yáº¿u tá»‘ rá»§i ro) â†’ panel 09 Bull/Base/Bear + Risk.
- Má»¥c 8 (káº¿ hoáº¡ch theo dÃµi, trigger tÃ­ch cá»±c/tiÃªu cá»±c) + disclaimer â†’ panel 10 Action Checklist/Disclaimer.

CÃCH VIáº¾T:
- CÃ³ thá»ƒ rÃºt gá»n cÃ¢u dÃ i thÃ nh bullet ngáº¯n nhÆ°ng khÃ´ng Ä‘Æ°á»£c xÃ³a Ã½.
- Chuyá»ƒn Ä‘oáº¡n vÄƒn thÃ nh báº£ng/biá»ƒu/matrix/checklist khi cÃ³ thá»ƒ.
- Má»i sá»‘ liá»‡u, nhÃ£n tráº¡ng thÃ¡i, nguá»“n, cáº£nh bÃ¡o pháº£i giá»¯ nguyÃªn.
- Æ¯u tiÃªn rÃµ rÃ ng, sÃºc tÃ­ch, Ä‘áº§y Ä‘á»§ hÆ¡n lÃ  Ä‘áº¹p nhÆ°ng thiáº¿u ná»™i dung.
""".strip()

FOCUS_PROMPT = (
    "Báº®T BUá»˜C KHÃ“A LAYOUT: chá»‰ táº¡o TRANG Dá»ŒC / PORTRAIT / LONG PORTRAIT. Cáº¤M landscape/trang ngang, cáº¥m 16:9 ngang, cáº¥m slide deck ngang. Náº¿u cÃ´ng cá»¥ Ä‘á»‹nh táº¡o landscape thÃ¬ pháº£i chuyá»ƒn sang A4 portrait hoáº·c long portrait trÆ°á»›c khi xuáº¥t. "
    "MODEL 3 OUTPUT CHO NOTEBOOKLM: táº¡o ÄÃšNG 2 TRANG Dá»ŒC DÃ€I / EXACTLY TWO-PAGE LONG PORTRAIT INFOGRAPHIC Ä‘á»™ phÃ¢n giáº£i cao theo Ä‘Ãºng áº£nh máº«u, KHÃ”NG lÃ m slide thuyáº¿t trÃ¬nh thÆ°a. "
    "Náº¿u cÃ´ng cá»¥ xuáº¥t slide/PDF, hÃ£y coi toÃ n bá»™ output lÃ  má»™t bÃ¡o cÃ¡o dá»c dÃ i liÃªn tá»¥c gá»“m Ä‘Ãºng 2 trang: Trang 1 panel 01-05, Trang 2 panel 06-10. Cáº¤M 1 trang, Cáº¤M 3+ trang, Cáº¤M landscape. "
    "Má»—i trang pháº£i cÃ³ nhiá»u báº£ng/Ã´ nhá» rÃµ rÃ ng, xáº¿p dáº¡ng lÆ°á»›i compact, Ä‘áº§y Ä‘á»§ ná»™i dung, Ã­t chá»¯, nhiá»u hÃ¬nh áº£nh/visual/smartart. "
    "Phong cÃ¡ch áº£nh máº«u: A4/portrait hoáº·c long portrait infographic/dashboard cao cáº¥p, ná»n xanh navy/blue-gradient, "
    "nhiá»u panel nhá» viá»n sÃ¡ng, header lá»›n á»Ÿ trÃªn, báº£ng nhá» xáº¿p dáº¡ng lÆ°á»›i, font nhá» nhÆ°ng rÃµ, one-page fact sheet/report chá»© KHÃ”NG pháº£i slide thuyáº¿t trÃ¬nh thÆ°a. "
    "ToÃ n trang pháº£i giá»‘ng institutional equity research infographic: nhiá»u thÃ´ng tin, nhiá»u báº£ng, nhiá»u badge/status, Ã­t khoáº£ng tráº¯ng, cÃ³ hÃ¬nh áº£nh/visual hooks thu hÃºt ngÆ°á»i Ä‘á»c. "
    "Báº®T BUá»˜C giá»¯ Ä‘á»§ ná»™i dung quan trá»ng, sá»‘ liá»‡u, nguá»“n, cáº£nh bÃ¡o; Ä‘áº·c biá»‡t khÃ´ng Ä‘Æ°á»£c bá» cÃ¡c chá»‰ bÃ¡o ká»¹ thuáº­t cÃ³ trong DOCX: giÃ¡/EOD, volume, MA, RSI, MACD, ADX/DI, Bollinger, Ichimoku, ROC/ret5, há»— trá»£/khÃ¡ng cá»±/RS, target/mean/median náº¿u cÃ³. KhÃ´ng bá»‹a vÃ  khÃ´ng láº¥y dá»¯ liá»‡u ngoÃ i. "
    "\n\nYÃŠU Cáº¦U VISUAL GIá»NG áº¢NH MáºªU: "
    "dÃ¹ng hero visual á»Ÿ header (biá»ƒu tÆ°á»£ng cá»• phiáº¿u/doanh nghiá»‡p/market, Ä‘Æ°á»ng line chart phÃ¡t sÃ¡ng, candlestick/arrow/magnifier icon), "
    "dÃ¹ng icon nhá» cho tá»«ng panel (news, macro, technical, valuation, risk, checklist), dÃ¹ng mini chart/sparkline/gauge/donut/heatmap khi cÃ³ thá»ƒ, "
    "dÃ¹ng background decorations tinh táº¿ nhÆ° glow, grid lines, wave/curve, faint stock chart watermark. "
    "KhÃ´ng Ä‘Æ°á»£c chá»‰ lÃ  báº£ng chá»¯ Ä‘Æ¡n Ä‘iá»‡u. Má»—i trang cáº§n Ã­t nháº¥t 3-5 yáº¿u tá»‘ visual: icon, mini chart, gauge, heatmap, arrow flow, badge, hoáº·c watermark. "
    "\n\nBá» Cá»¤C Báº®T BUá»˜C: top title bar + subtitle/data freshness; dÆ°á»›i lÃ  KPI strip nhá»; thÃ¢n trang chia 2-3 cá»™t; Ä‘Ãºng tinh tháº§n 10 mini panels/cards. "
    "10 Ã´ gá»“m: 01 Header/Hero, 02 Executive Summary, 03 KPI Snapshot, 04 News/Catalyst Timeline, 05 Market/Sector Context, 06 Technical Matrix, 07 LH Strategy Box, 08 Fundamental/Valuation, 09 Bull/Base/Bear + Risk, 10 Action Checklist/Disclaimer. "
    "Má»—i panel cÃ³ title bar nhá», icon/badge mÃ u, bullet ngáº¯n hoáº·c báº£ng 2-4 cá»™t. "
    "Giáº£m kÃ­ch thÆ°á»›c chá»¯ vÃ  Ã´/card: KHÃ”NG dÃ¹ng KPI card quÃ¡ bá»±, KHÃ”NG Ä‘á»ƒ khoáº£ng tráº¯ng lá»›n, KHÃ”NG dÃ¹ng 1-2 card chiáº¿m ná»­a trang. "
    "ToÃ n output pháº£i cÃ³ máº­t Ä‘á»™ thÃ´ng tin cao: tá»‘i thiá»ƒu 10 khá»‘i thÃ´ng tin nhá», nhiá»u báº£ng/matrix; dÃ¹ng compact grid 2 cá»™t/3 cá»™t, mini table, mini badge, mini sparkline/gauge náº¿u cÃ³. KhÃ´ng Ä‘Æ°á»£c táº¡o trang chá»‰ cÃ³ tiÃªu Ä‘á» + vÃ i bullet. "
    "Æ¯u tiÃªn Báº¢NG/BIá»‚U/CARD nhá» gá»n thay vÃ¬ Ä‘oáº¡n vÄƒn dÃ i: KPI strip nhá», timeline tin tá»©c, news-impact table, technical indicator matrix, valuation table, "
    "peer comparison náº¿u cÃ³, valuation scorecard, bull/base/bear scenario matrix, risk probability-impact matrix, catalyst checklist, trade plan checklist, data-quality box. "
    "Viáº¿t bullet cá»±c ngáº¯n nhÆ°ng khÃ´ng máº¥t Ã½; má»—i Ã´/card chá»©a nhiá»u dÃ²ng ngáº¯n. Náº¿u khÃ´ng Ä‘á»§ chá»— thÃ¬ tÄƒng sá»‘ trang, khÃ´ng Ä‘Æ°á»£c lÃ m máº¥t ná»™i dung. "
    "\n\nSTYLE MÃ€U: ná»n navy/blue-gradient giá»‘ng infographic máº«u (#071B3A, #0B2A5B, #123B7A), panel xanh Ä‘áº­m, viá»n cyan/blue, chá»¯ tráº¯ng/xanh nháº¡t, "
    "accent cyan/vÃ ng/cam/Ä‘á»/xanh lÃ¡; dÃ¹ng glow/neon nháº¹, icon line-art, nhÃ£n mÃ u tÃ­ch cá»±c/tiÃªu cá»±c/trung tÃ­nh/rá»§i ro. "
    "Káº¿t quáº£ mong muá»‘n: 2 trang dá»c dÃ i Ä‘á»™ phÃ¢n giáº£i cao, nhÃ¬n nhÆ° infographic/report/dashboard phÃ¢n tÃ­ch cá»• phiáº¿u giÃ u dá»¯ liá»‡u, cÃ³ hÃ¬nh áº£nh thu hÃºt nhÆ° áº£nh máº«u, khÃ´ng pháº£i slide marketing vÃ  khÃ´ng pháº£i báº£ng chá»¯ xáº¥u/sÆ¡ sÃ i. "
    "KhÃ´ng pháº£i khuyáº¿n nghá»‹ Ä‘áº§u tÆ° cÃ¡ nhÃ¢n hÃ³a."
)



def _profile_pool() -> list[str]:
    raw = os.environ.get("NLM_PROFILE_POOL") or os.environ.get("NOTEBOOKLM_PROFILE_POOL") or ""
    return [x.strip() for x in re.split(r"[,;\s]+", raw) if x.strip()]


def _select_profile() -> str | None:
    pool = _profile_pool()
    if not pool:
        return os.environ.get("NLM_PROFILE") or os.environ.get("NOTEBOOKLM_PROFILE") or None
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    idx = 0
    try:
        data = json.loads(PROFILE_STATE.read_text(encoding="utf-8")) if PROFILE_STATE.exists() else {}
        idx = int(data.get("idx", 0))
    except Exception:
        idx = 0
    profile = pool[idx % len(pool)]
    try:
        PROFILE_STATE.write_text(json.dumps({"idx": idx + 1, "last_profile": profile, "pool": pool}, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return profile


def _with_profile(args: list[str], profile: str | None = None) -> list[str]:
    prof = profile or _ACTIVE_PROFILE
    if not prof:
        return args
    # login has its own --profile option; other commands also expose --profile.
    if "--profile" in args or "-p" in args:
        return args
    return [*args, "--profile", prof]

def cleanup_temp(max_age_days: int = 3) -> None:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - max_age_days * 86400
    for p in TEMP_DIR.glob("*"):
        try:
            if p.is_file() and p.stat().st_mtime < cutoff:
                p.unlink()
        except Exception:
            pass


_ACTIVE_PROFILE: str | None = None

def _run_once(args: list[str], timeout: int = 900) -> tuple[int, str]:
    if not NLM.exists():
        raise FileNotFoundError(f"nlm.exe not found: {NLM}")
    proc = subprocess.run([str(NLM), *_with_profile(args)], text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=timeout)
    out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return proc.returncode, out


def _is_stale_auth_output(out: str) -> bool:
    low = (out or "").lower()
    return "authentication expired" in low or ("auth" in low and ("expired" in low or "stale" in low))


def notebooklm_auth_check(auto_login: bool = True, timeout: int = 360) -> dict[str, Any]:
    """Validate NotebookLM CLI auth and re-login with the saved browser session if needed.

    This is intentionally safe for dashboard/export use: it first performs a cheap
    `notebook list --json`, then `auth refresh`, then `login` only when the CLI says
    auth is expired/stale. On HÃ²a Äáº¡i ka's machine Chrome already has the account, so
    login normally completes without asking for the password again.
    """
    code, out = _run_once(["notebook", "list", "--json"], timeout=120)
    if code == 0:
        return {"ok": True, "stage": "list", "message": "NotebookLM auth OK"}
    last = out[-2000:]
    if not _is_stale_auth_output(out):
        return {"ok": False, "stage": "list", "error": last}

    _run_once(["auth", "refresh"], timeout=120)
    time.sleep(2)
    code, out = _run_once(["notebook", "list", "--json"], timeout=120)
    if code == 0:
        return {"ok": True, "stage": "refresh", "message": "NotebookLM auth refreshed"}
    last = out[-2000:]
    if not auto_login:
        return {"ok": False, "stage": "refresh", "error": last}

    code, out = _run_once(["login"], timeout=timeout)
    if code != 0:
        return {"ok": False, "stage": "login", "error": out[-2000:]}
    code, out = _run_once(["notebook", "list", "--json"], timeout=120)
    if code == 0:
        return {"ok": True, "stage": "login", "message": "NotebookLM re-login OK"}
    return {"ok": False, "stage": "verify_after_login", "error": out[-2000:]}


def _is_rate_limited_output(out: str) -> bool:
    low = str(out or "").lower()
    return any(x in low for x in ("rate limited", "resource_exhausted", "rpc rate limit", "code 8"))


def _run(args: list[str], timeout: int = 900) -> str:
    code, out = _run_once(args, timeout=timeout)
    if code == 0:
        return out.strip()
    stale = _is_stale_auth_output(out)
    if stale:
        auth = notebooklm_auth_check(auto_login=True)
        if auth.get("ok"):
            code2, out2 = _run_once(args, timeout=timeout)
            if code2 == 0:
                return out2.strip()
            out = out2
            code = code2
        else:
            out = f"{out}\n\nAUTO_AUTH_FAILED: {auth}"
    if _is_rate_limited_output(out):
        delays = [60, 120, 240]
        last = out
        code2 = code
        for delay in delays:
            time.sleep(delay)
            code2, out2 = _run_once(args, timeout=timeout)
            if code2 == 0:
                return out2.strip()
            last = out2
            if not _is_rate_limited_output(out2):
                break
        out = f"NOTEBOOKLM_RATE_LIMIT: NotebookLM đang giới hạn tạo slide/PDF; đã retry {sum(delays)}s. Chi tiết: {last[-1600:]}"
        code = code2
    raise RuntimeError(f"nlm {' '.join(args)} failed ({code}): {out[-2000:]}")

def _extract_id(text: str) -> str:
    try:
        d = json.loads(text)
        if isinstance(d, dict):
            for key in ("id", "notebook_id", "uuid", "notebookId"):
                if d.get(key):
                    return str(d[key])
            if isinstance(d.get("notebook"), dict):
                for key in ("id", "uuid"):
                    if d["notebook"].get(key):
                        return str(d["notebook"][key])
    except Exception:
        pass
    m = re.search(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", text)
    if m:
        return m.group(0)
    raise ValueError(f"Cannot extract NotebookLM id from: {text[:1000]}")


def _pdf_quality_score(pdf_path: Path) -> dict[str, Any]:
    """Best-effort density check. NotebookLM controls visuals, but reject obviously sparse decks."""
    info: dict[str, Any] = {"checked": False, "pages": 0, "text_chars": 0, "ok": True, "reason": ""}
    try:
        from PyPDF2 import PdfReader  # type: ignore
        reader = PdfReader(str(pdf_path))
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                pass
        info["checked"] = True
        info["pages"] = len(reader.pages)
        info["text_chars"] = sum(len(t.strip()) for t in texts)
        # Model 3 target: one-page/long-infographic style, dense enough to preserve content.
        # NotebookLM may still export 1-2 PDF pages; accept if text density is high.
        pages = int(info["pages"] or 0)
        chars = int(info["text_chars"] or 0)
        portrait_ok = True
        dims = []
        try:
            for page in reader.pages:
                box = page.mediabox
                w = float(box.width); h = float(box.height)
                dims.append([round(w, 1), round(h, 1)])
                if w > h:
                    portrait_ok = False
        except Exception:
            pass
        full_text = "\n".join(texts)
        utf8_report = vietnamese_quality_report(full_text)
        info["page_dims"] = dims
        info["portrait_ok"] = portrait_ok
        info["utf8_report"] = utf8_report
        info["ok"] = bool(pages == 2 and chars >= 1800 and portrait_ok and not utf8_report.get("mojibake_markers") and not utf8_report.get("replacement_chars"))
        if not info["ok"]:
            info["reason"] = f"not dense 2-page portrait/utf8 clean enough: pages={pages}, text_chars={chars}, portrait_ok={portrait_ok}, dims={dims}, utf8={utf8_report}"
    except Exception as exc:
        try:
            import fitz  # type: ignore
            doc = fitz.open(str(pdf_path))
            dims=[]; portrait_ok=True
            for page in doc:
                w=float(page.rect.width); h=float(page.rect.height)
                dims.append([round(w,1), round(h,1)])
                if w > h:
                    portrait_ok=False
            info["checked"] = True
            info["pages"] = len(doc)
            info["text_chars"] = sum(len((page.get_text() or "").strip()) for page in doc)
            full_text = "\n".join((page.get_text() or "") for page in doc)
            utf8_report = vietnamese_quality_report(full_text)
            info["page_dims"] = dims
            info["portrait_ok"] = portrait_ok
            info["utf8_report"] = utf8_report
            pages=int(info["pages"] or 0); chars=int(info["text_chars"] or 0)
            info["ok"] = bool(pages == 2 and chars >= 1800 and portrait_ok and not utf8_report.get("mojibake_markers") and not utf8_report.get("replacement_chars"))
            if not info["ok"]:
                info["reason"] = f"not dense 2-page portrait/utf8 clean enough: pages={pages}, text_chars={chars}, portrait_ok={portrait_ok}, dims={dims}, utf8={utf8_report}"
        except Exception as exc2:
            info["ok"] = False
            info["reason"] = f"quality check failed: {type(exc).__name__}: {exc}; fallback {type(exc2).__name__}: {exc2}"
    return info


def create_presentation_from_docx(docx_path: str, title: str = "LHInvestment Model 3 Report") -> dict[str, Any]:
    global _ACTIVE_PROFILE
    _ACTIVE_PROFILE = _select_profile()
    cleanup_temp(3)
    docx = Path(docx_path)
    if not docx.exists():
        raise FileNotFoundError(docx)

    nb_out = _run(["notebook", "create", title, "--json"], timeout=120)
    notebook_id = _extract_id(nb_out)

    _run(["source", "add", notebook_id, "--file", str(docx), "--wait", "--wait-timeout", "600"], timeout=900)

    # Nháº­p prompt trá»±c tiáº¿p vÃ o bÆ°á»›c táº¡o trang trÃ¬nh bÃ y (--focus), khÃ´ng thÃªm prompt nhÆ° má»™t source
    # Ä‘á»ƒ trÃ¡nh NotebookLM Ä‘Æ°a ná»™i dung chá»‰ dáº«n vÃ o slide nhÆ° dá»¯ liá»‡u bÃ¡o cÃ¡o.
    base_prompt = repair_vietnamese_text(f"{FOCUS_PROMPT}\n\n{NOTEBOOKLM_STOCK_PROMPT}")
    retry_prompt = base_prompt + (
        "\n\nKIá»‚M TRA CHáº¤T LÆ¯á»¢NG Báº®T BUá»˜C CHO MODEL 3: náº¿u báº£n trÆ°á»›c ra nhiá»u slide/trang thÆ°a, báº£ng/card quÃ¡ bá»±, chá»¯ quÃ¡ bá»±, Ã­t ná»™i dung hoáº·c lá»—i mojibake/Unicode, "
        "hÃ£y táº¡o láº¡i thÃ nh Ä‘Ãºng 2 trang dá»c dÃ i dense hÆ¡n: Trang 1 panel 01-05, Trang 2 panel 06-10, nhiá»u visual/smartart/icon/mini chart hÆ¡n, giáº£m khoáº£ng tráº¯ng, giá»¯ Ä‘á»§ ná»™i dung quan trá»ng. "
        "KhÃ´ng bung thÃ nh deck ngang hoáº·c hÆ¡n 2 trang náº¿u khÃ´ng báº¯t buá»™c. Báº®T BUá»˜C tiáº¿ng Viá»‡t Unicode sáº¡ch, khÃ´ng mojibake."
    )

    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", title)[:60].strip("-") or "notebooklm-slide-deck"
    last_err = ""
    last_quality: dict[str, Any] = {}
    for attempt, prompt in enumerate((base_prompt, retry_prompt), 1):
        # Model 3: yÃªu cáº§u Ä‘Ãºng 2 trang dá»c dense; dÃ¹ng detailed_deck nhÆ°ng focus Ã©p two-page portrait / 10 panels.
        _run(["slides", "create", notebook_id, "--format", "detailed_deck", "--length", "short", "--language", "vi", "--focus", prompt, "--confirm"], timeout=900)
        out_pdf = TEMP_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{safe}-attempt{attempt}.pdf"
        for _ in range(30):
            try:
                _run(["download", "slide-deck", notebook_id, "--output", str(out_pdf), "--format", "pdf", "--no-progress"], timeout=300)
                if out_pdf.exists() and out_pdf.stat().st_size > 0:
                    # Tá»± Ä‘á»™ng xÃ³a watermark "NotebookLM + icon" gÃ³c pháº£i dÆ°á»›i má»—i trang.
                    try:
                        from pdf_watermark_cleaner import strip_notebooklm_watermark
                        strip_notebooklm_watermark(out_pdf)
                    except Exception:
                        pass  # thiáº¿u PyMuPDF/Pillow thÃ¬ giá»¯ nguyÃªn PDF, khÃ´ng cháº·n pipeline
                    last_quality = _pdf_quality_score(out_pdf)
                    if last_quality.get("ok", True) or attempt == 2:
                        return {"ok": bool(last_quality.get("ok", True)), "profile": _ACTIVE_PROFILE, "notebook_id": notebook_id, "slide_pdf": str(out_pdf), "quality": last_quality, "attempt": attempt}
                    last_err = str(last_quality.get("reason") or "deck quality too sparse")
                    break
            except Exception as exc:
                last_err = str(exc)
            time.sleep(20)
    return {"ok": False, "profile": _ACTIVE_PROFILE, "notebook_id": notebook_id, "error": last_err, "quality": last_quality}

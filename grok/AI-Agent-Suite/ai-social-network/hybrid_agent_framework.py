"""SuperLH optimized workflows.

Commands:
- /model1 <task>: cost-efficient main flow, no Claude by default.
- /model1 premium <task>: adds Claude brainstorm and Claude final review.
- /model2 <task>: compact debate.
- /model2 full <task>: fuller multi-AI debate.
- /model2 grok <task>: debate with Grok terminal included.
- /model3 <task>: TradingAgents-inspired HTML report, no Claude by default.
- /model3 premium <task>: adds Claude final review.

All prompts are UTF-8 Vietnamese. Keep this file saved as UTF-8.
"""
from __future__ import annotations

import concurrent.futures
import importlib.util
import json
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import httpx

from app.providers import get_text_agent
from model3_lhinvestment_context import build_lhinvestment_context
from model3_docx_formatter import write_model3_docx
from vietnamese_text_guard import has_vietnamese_quality_issue, repair_vietnamese_text, clean_vietnamese_object, vietnamese_quality_report

ProgressFn = Callable[[str], None]

os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-dummy-crewai-construction-only"

AGENT_TIMEOUT_SECONDS = int(os.environ.get("SUPERLH_AGENT_TIMEOUT_SECONDS", "0"))
AGENT_TICK_SECONDS = int(os.environ.get("SUPERLH_AGENT_TICK_SECONDS", "120"))
AGENT_STUCK_WARN_SECONDS = int(os.environ.get("SUPERLH_AGENT_STUCK_WARN_SECONDS", "300"))
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=16, thread_name_prefix="superlh-agent")

try:
    from crewai import Agent as CrewAIAgent, Task as CrewAITask, Crew as CrewAICrew
except Exception:  # noqa: BLE001
    CrewAIAgent = CrewAITask = CrewAICrew = None  # type: ignore[assignment]

try:
    from agent_framework import AgentResponse, AgentSession
    from agent_framework_orchestrations import GroupChatBuilder
except Exception:  # noqa: BLE001
    AgentResponse = AgentSession = GroupChatBuilder = None  # type: ignore[assignment]


@dataclass
class AgentStep:
    agent_id: str
    label: str
    role: str
    goal: str
    speak_to: str
    task_template: str


def step(agent_id: str, label: str, role: str, goal: str, speak_to: str, template: str) -> AgentStep:
    return AgentStep(agent_id, label, role, goal, speak_to, template)


CLAUDE_BRAINSTORM = step(
    "claude", "Claude Premium Brainstorm", "Chiến lược gia cao cấp",
    "Dựng khung chiến lược, tiêu chí đúng/sai và các rủi ro lớn.", "Kiro/Codex",
    "Brainstorm chiến lược cho nhiệm vụ. Nêu dữ kiện, giả định, tiêu chí đúng/sai, rủi ro lớn.\n\nNhiệm vụ:\n{task}\n\nBối cảnh:\n{context}",
)
KIRO_DISPATCH = step(
    "kiro", "Kiro Dispatcher", "Điều phối viên tiết kiệm",
    "Chia việc cho Codex phân tích chính và Kiro frontend/checklist; không dùng Grok trong flow chính.", "Codex + Kiro Frontend",
    "Phân tích nhiệm vụ và chia 2 nhánh song song:\n"
    "1) Codex: phân tích chính/hard work/tính toán/code nếu có.\n"
    "2) Kiro Frontend: bố cục output, checklist, cảnh báo, format/HTML nếu cần.\n"
    "Không giao Grok trong flow chính. Nêu tiêu chí Codex test sau cùng.\n\nNhiệm vụ:\n{task}\n\nBối cảnh:\n{context}",
)
CODEX_HARD = step(
    "chatgpt", "Codex Hard Analysis", "Workhorse phân tích chính",
    "Làm phần khó nhất: phân tích, tính toán, code, synthesis; không bịa dữ liệu.", "Codex Test",
    "Bạn là Codex. Làm phần phân tích chính/hard work theo phân công. Nếu thiếu dữ liệu, nói rõ; không tự bịa.\n\nNhiệm vụ:\n{task}\n\nBối cảnh:\n{context}",
)
KIRO_FRONTEND = step(
    "kiro", "Kiro Frontend/Checklist", "Frontend và checklist",
    "Tạo bố cục kết quả, bảng/bullets, checklist, cảnh báo, format hoặc HTML nếu cần.", "Codex Test",
    "Bạn là Kiro. Tạo cấu trúc output/frontend/checklist rõ ràng: summary, bảng/bullets, cảnh báo, checklist kiểm chứng.\n\nNhiệm vụ:\n{task}\n\nBối cảnh:\n{context}",
)
CODEX_TEST = step(
    "chatgpt", "Codex Test Cases", "Người kiểm thử",
    "Kiểm số liệu, logic, format, edge cases và phần simple-check thay Grok.", "Claude hoặc người dùng",
    "Bạn là Codex tester. Kiểm toàn bộ kết quả: số liệu, logic, format, edge cases, giả định thiếu. Nêu PASS/FAIL và bản sửa cuối.\n\nNhiệm vụ:\n{task}\n\nBối cảnh:\n{context}",
)
CLAUDE_FINAL = step(
    "claude", "Claude Premium Final Review", "Chủ tọa cao cấp",
    "Review cuối khi premium: sửa lỗi, chốt câu trả lời chất lượng cao.", "Người dùng",
    "Review cuối và chốt đáp án. Nếu có lỗi trong test, sửa trước khi chốt. Trả lời ngắn gọn, chính xác.\n\nNhiệm vụ:\n{task}\n\nBối cảnh:\n{context}",
)

MODEL2_COMPACT = [
    step("chatgpt", "Codex Position", "Bên lập luận chính", "Đưa lời giải chính, cấu trúc tốt.", "Kiro", "Đưa lời giải chính cho nhiệm vụ. Nêu giả định và điểm cần kiểm.\n\nNhiệm vụ:\n{task}\n\nBiên bản:\n{context}"),
    step("kiro", "Kiro Critique", "Bên phản biện checklist", "Phản biện bằng checklist/rủi ro/điểm thiếu.", "Codex", "Phản biện câu trả lời Codex: thiếu gì, sai gì, rủi ro gì, cần sửa gì.\n\nNhiệm vụ:\n{task}\n\nBiên bản:\n{context}"),
    step("chatgpt", "Codex Revision", "Bên sửa luận điểm", "Sửa lại sau phản biện Kiro.", "Claude", "Sửa câu trả lời sau phản biện Kiro. Nêu bản revised cuối.\n\nNhiệm vụ:\n{task}\n\nBiên bản:\n{context}"),
    CLAUDE_FINAL,
]
MODEL2_FULL_BASE = [
    step("claude", "Claude Viewpoint", "AI chiến lược", "Đưa khung đúng/sai và điểm lớn.", "Các AI khác", "Đưa quan điểm chiến lược cho nhiệm vụ.\n\nNhiệm vụ:\n{task}\n\nBiên bản:\n{context}"),
    step("chatgpt", "Codex Viewpoint", "AI hard solver", "Đưa lời giải chính, phân tích sâu.", "Các AI khác", "Đưa quan điểm Codex, đồng ý/phản biện Claude nếu cần.\n\nNhiệm vụ:\n{task}\n\nBiên bản:\n{context}"),
    step("kiro", "Kiro Viewpoint", "AI PM/QA", "Checklist, rủi ro, triển khai.", "Các AI khác", "Đưa quan điểm Kiro: checklist, rủi ro, triển khai, điểm thiếu.\n\nNhiệm vụ:\n{task}\n\nBiên bản:\n{context}"),
    step("gemini", "Gemini Viewpoint", "AI góc nhìn bổ sung", "Góc nhìn thay thế/creative/multimodal nếu cần.", "Các AI khác", "Đưa quan điểm Gemini: góc nhìn khác, điểm thiếu, đánh giá các quan điểm trước.\n\nNhiệm vụ:\n{task}\n\nBiên bản:\n{context}"),
]
GROK_VIEW = step("grok", "Grok Viewpoint", "AI phản biện terminal", "Phản biện sâu nhưng chậm/dễ kẹt; chỉ chạy khi được gọi.", "Các AI khác", "Đưa quan điểm Grok: phản biện thẳng, tính lại nếu có số liệu, nêu verdict độc lập.\n\nNhiệm vụ:\n{task}\n\nBiên bản:\n{context}")
KIRO_JUDGE = step("kiro", "Kiro Debate Judge", "Trọng tài", "Chấm đồng thuận/bất đồng và lập luận đáng tin nhất.", "Claude", "Chấm cuộc tranh luận: điểm đồng thuận, bất đồng, lập luận đáng tin nhất, lỗi còn lại.\n\nNhiệm vụ:\n{task}\n\nBiên bản:\n{context}")
CLAUDE_DEBATE_FINAL = step("claude", "Claude Debate Final", "Chủ tọa", "Chốt kết quả cuối từ tranh luận.", "Người dùng", "Chốt câu trả lời cuối từ tranh luận. Ngắn gọn, chính xác, nêu điều chưa chắc nếu có.\n\nNhiệm vụ:\n{task}\n\nBiên bản:\n{context}")

MODEL3_QUICK_SUMMARY = step(
    "kiro", "Kiro Quick Summary", "Quick-summary analyst",
    "Viết phần tóm tắt nhanh của báo cáo từ dữ liệu đã có; ngắn, sạch, không bịa số liệu.", "Word template",
    "Bạn là Kiro. Viết PHẦN 1 — TÓM TẮT NHANH cho báo cáo Super_LH.\n"
    "Chỉ viết summary ngắn theo dữ liệu context: quan điểm, điểm chính, rủi ro chính, việc cần theo dõi. Không bịa số liệu.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)

MODEL3_NEWS = step(
    "grok", "GrokX News & Impact", "News/direct-impact analyst",
    "GrokX viết phần tin tức và phân tích tác động từ tin tức; chỉ dùng tin trực tiếp và trả kết quả sạch.", "Word template",
    "Bạn là GrokX News Analyst cho báo cáo cổ phiếu.\n"
    "OUTPUT BẮT BUỘC: bọc phần kết quả cuối trong START_RESULT và END_RESULT; không đưa log search/thinking/tool vào marker.\n"
    "Dùng đúng prompt của Hòa Đại ka cho mã cổ phiếu trong nhiệm vụ, chỉ thay ticker X:\n"
    "Tìm web và trả lời tiếng Việt có dấu. Lấy tối đa 5 tin năm 2026 liên quan TRỰC TIẾP cổ phiếu X. Ưu tiên KQKD, doanh thu/lợi nhuận, kế hoạch. Mỗi tin gồm 2 câu: tóm tắt 1 câu, đánh giá tác động cổ phiếu tăng/giảm/trung tính bao nhiêu % và vì sao. Nếu không đủ 5 tin trực tiếp thì chỉ trả số tin tìm được và ghi rõ thiếu nguồn trực tiếp. Không bịa.\n\n"
    "Bối cảnh có thể gồm TRADINGAGENTS_NEWS_CONTEXT và WEB_SEARCH_CONTEXT do hệ thống tìm hộ, nhưng kết quả xuất báo cáo phải do Grok chọn/lọc theo prompt trên. KHÔNG ràng buộc source: được dùng mọi nguồn công khai phù hợp như CafeF, Vietstock, 24HMoney, FireAnt, Mekong ASEAN, báo chí, website doanh nghiệp, CTCK, không block nguồn nào.\n"
    "Quy tắc bắt buộc:\n"
    "- CHỈ lấy tin tác động trực tiếp đến doanh nghiệp/cổ phiếu trong task: KQKD, doanh thu/lợi nhuận, triển vọng tăng trưởng, kế hoạch lợi nhuận, định giá/khuyến nghị/target, tín dụng/NIM/nợ xấu với ngân hàng, margin/tự doanh/thị phần với CTCK, cổ tức/phát hành/tăng vốn/ESOP, pháp lý, lãnh đạo, M&A/đối tác, sản phẩm/chuỗi/cửa hàng ảnh hưởng trực tiếp.\n"
    "- LOẠI BỎ tin chỉ là thị trường chung, dòng tiền, VN-Index, nhóm ngành, danh sách cổ phiếu đáng chú ý, chứng quyền/ETF, hoặc bài chỉ nhắc mã mà không nói về KQKD/triển vọng/capital/rủi ro riêng của doanh nghiệp.\n"
    "- Không được bù đủ số lượng bằng tin thị trường. Nếu chỉ tìm được 1-2 tin trực tiếp thì ghi 1-2 tin và nói rõ thiếu nguồn trực tiếp.\n"
    "- Mỗi tin đúng 3 câu ngắn gọn: (1) Tóm tắt tin tức. (2) Dựa trên dữ kiện của tin tức đánh giá cổ phiếu tăng/giảm bao nhiêu %. (3) Giải thích cực ngắn vì sao.\n"
    "- Chọn đúng 5 tin trực tiếp nhất, khác nội dung nhau; nếu không đủ 5 thì ghi rõ thiếu nguồn trực tiếp, không bịa.\n"
    "- Nếu chỉ có title/snippet/link thì phân tích dựa trên title/snippet và ghi rõ. Không giả vờ đã browse sâu hơn.\n"
    "- Không viết phần mở đầu/phương pháp dài; đi thẳng vào danh sách tin và kết luận sentiment ngắn.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)
MODEL3_IMPACT = step(
    "grok", "GrokX News & Sentiment Impact", "News/sentiment analyst",
    "Tin tức và phân tích tác động từ tin tức do GrokX viết; mỗi tin 1 dòng giải thích.", "Codex Technical/Macro",
    "Bạn là Codex News/Sentiment Analyst. Dựa trên phần tin tức Kiro đã tổng hợp, đánh giá tác động của từng tin đến cổ phiếu và sentiment tổng thể.\n"
    "Yêu cầu bắt buộc:\n"
    "- Mỗi tin đúng 1 dòng: [Tích cực/Tiêu cực/Trung tính] - giải thích ngắn vì sao ảnh hưởng đến giá/kỳ vọng/lợi nhuận/rủi ro.\n"
    "- Sau danh sách tin, thêm mục Sentiment tổng thể: Bullish/Bearish/Neutral + lý do.\n"
    "- Không thêm tin mới nếu không có trong bối cảnh.\n"
    "- Nếu tin chưa đủ nguồn hoặc chưa rõ tác động, ghi Trung tính/Chưa rõ và lý do.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)
MODEL3_ANALYSIS = step(
    "chatgpt", "Codex LHInvestment Indicator Matrix", "TA indicator analyst",
    "Codex viết LHInvestmentIndicator Matrix — chỉ báo bắt buộc; bỏ phần giá, hỗ trợ, MA, Volume trong bảng đầu tiên.", "Kiro Scenario",
    "Bạn là Codex analyst cho Model 3 FAST. Kiro đã xử lý news/vĩ mô; bạn xử lý phần còn lại để ra research pack cho DOCX/HTML.\n"
    "UTF-8 STRICT: bắt buộc trả tiếng Việt có dấu đầy đủ. Không dùng tiếng Việt không dấu kiểu 'phan tich/co phieu/du lieu/ket luan'. Không xuất mojibake. Nếu provider không giữ được dấu, hãy ưu tiên dùng thuật ngữ tiếng Anh thay vì tiếng Việt mất dấu.\n"
    "1) Phân tích kỹ thuật/LHInvestment indicators: PHẢI đưa bảng chỉ báo LHInvestment rõ ràng, không được bỏ.\n"
    "   - Bắt buộc rà soát context và xuất bảng 'LHINVESTMENT INDICATOR MATRIX' gồm: Giá/EOD, asOfDate, % thay đổi, volume, avgVol20, volumeRatio, MA10/20/50/100/200, RSI14, MACD, MACD signal, MACD histogram, ADX, +DI, -DI, Bollinger upper/mid/lower/bbPercent, Ichimoku Tenkan/Kijun/Cloud nếu có, ROC20/ret5, hỗ trợ, kháng cự, RS levels, stop/invalid, rankScore/buyScore/riskScore nếu có.\n"
    "   - Ngoài bảng raw indicator, BẮT BUỘC chia thành 4 CẶP/NHÓM LHInvestment và mỗi cặp phải có nhận định riêng:\n"
    "     Cặp 1 — Xu hướng/MA: Price vs MA10/20/50/100/200 + cấu trúc xu hướng.\n"
    "     Cặp 2 — Động lượng: RSI + MACD + ROC/ret5 nếu có.\n"
    "     Cặp 3 — Sức mạnh xu hướng/dòng tiền: ADX + +DI/-DI + Volume/avgVol20/volumeRatio.\n"
    "     Cặp 4 — Biên dao động & vùng giá: Bollinger + Ichimoku nếu có + RS support/resistance.\n"
    "   - Mỗi cặp phải có: dữ liệu chính, nhãn Tích cực/Tiêu cực/Trung tính, nhận định riêng 2-3 câu, vùng giá/điều kiện xác nhận hoặc phủ định.\n"
    "   - Mỗi dòng bảng phải có 4 cột: Chỉ báo | Giá trị thật từ LHInvestment | Nhãn Tích cực/Tiêu cực/Trung tính | Ý nghĩa đầu tư/vùng theo dõi.\n"
    "   - Không liệt kê toàn bộ raw strategy records, không viết các mục Trend Pullback/TrendLH, không dùng giọng AI nói chuyện với nhau.\n"
    "   - Với mỗi chỉ báo có dữ liệu: ghi giá trị thật + giải thích rõ tác động đến xác suất hồi/giảm và vùng giá cần quan sát.\n"
    "   - Nếu thiếu chỉ báo nào, ghi rõ 'Không có trong LHInvestment context' thay vì bỏ qua âm thầm.\n"
    "2) Fundamental/valuation: phải khai thác tối đa Fundamental signals, Fundamental top upside/valuation, Yahoo Finance profile/summaryDetail/financialData/defaultKeyStatistics, 24hmoney report nếu có.\n"
    "   - Bắt buộc có bảng Fundamental gồm: business model/driver, doanh thu/lợi nhuận nếu có, EPS, P/E, P/B, ROE, ROA, biên lợi nhuận, nợ/vốn, target mean/median, upside/downside, catalyst cơ bản, data gaps.\n"
    "   - Nếu thiếu số nào thì ghi N/A và nêu nguồn đã thử: LH fundamental cache, 24hmoney, Yahoo Finance, broker/CTCK. Không được để mục fundamental trống chung chung.\n"
    "3) Phân tích kịch bản chuyên sâu cho NĐT: bắt buộc có Bull/Base/Bear case theo bảng. Mỗi kịch bản phải có: trigger/kích hoạt, điều kiện kỹ thuật, điều kiện tin tức/cơ bản, vùng giá theo dõi, xác suất/độ tin cậy định tính, hành động phù hợp, điểm invalidation.\n"
    "4) Bull/Bear/Risk: bull case, base case, bear case, catalysts, invalidation, risk score 1-5, stance, trade plan. Mỗi ý phải có nguyên nhân + tác động đầu tư + điều kiện theo dõi. Không viết chung chung.\n"
    "5) Output phải đủ dữ liệu để làm dense infographic: nhiều bảng/scorecard/matrix nhỏ, không viết sơ sài; nhưng dừng ở mục 7, không tạo mục 8/checklist dài phía sau.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)

MODEL3_FUNDAMENTAL = step(
    "chatgpt", "Codex Fundamental & Macro", "Fundamental/macro analyst",
    "Codex viết Fundamental và Macro, dựa trên data Macro/LHInvestment trong context; không bịa.", "Kiro Scenario",
    "Bạn là Codex Fundamental & Macro Analyst trong Super_LH.\n"
    "Dựa trên dữ liệu LHInvestment context, đặc biệt data Macro/LHInvestment và tin tức đã có, phân tích ngắn:\n"
    "- Business driver chính của doanh nghiệp/ngành.\n"
    "- KQKD/triển vọng lợi nhuận nếu context có nguồn.\n"
    "- Định giá P/E, P/B, upside/target nếu context có dữ liệu; nếu không có thì ghi thiếu.\n"
    "- Điểm mạnh cơ bản, điểm yếu cơ bản.\n"
    "- 3 câu hỏi cần kiểm chứng thêm trước khi ra quyết định.\n"
    "Không tự bịa số liệu hoặc target giá.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)
MODEL3_SCENARIO = step(
    "kiro", "Kiro Deep Investment Scenario", "Scenario analyst",
    "Kiro viết kịch bản đầu tư chuyên sâu dựa trên tin tức, indicator, fundamental và macro ở các phần trên.", "Codex Bull/Bear",
    "Bạn là Kiro. Viết PHẦN 5 — KỊCH BẢN ĐẦU TƯ CHUYÊN SÂU dựa trên toàn bộ phần trước.\n"
    "Có Bull/Base/Bear, trigger, điều kiện xác nhận/phủ định, hành động theo dõi. Không thêm số liệu mới nếu context không có.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)

MODEL3_BULL_BEAR = step(
    "chatgpt", "Codex Bull/Bear/Catalyst", "Bull-bear-catalyst analyst",
    "Codex viết Bull case — Bear case — Catalyst từ news, fundamental, LH technical và macro.", "Kiro Risk View",
    "Bạn là Codex Bull/Bear/Catalyst Analyst theo phong cách TradingAgents.\n"
    "Từ toàn bộ bối cảnh trước đó, tạo tranh luận nghiên cứu ngắn:\n"
    "- Bull case: 3-5 luận điểm mạnh nhất.\n"
    "- Bear case: 3-5 rủi ro/luận điểm phản biện mạnh nhất.\n"
    "- Catalysts cần theo dõi trong 1-4 tuần.\n"
    "- Invalidation: điều kiện nào làm luận điểm tích cực sai.\n"
    "- Data gaps: dữ liệu còn thiếu/cũ/cần refresh.\n"
    "Viết giọng dứt khoát theo dữ liệu; tránh các câu rào kiểu 'chỉ tham khảo'. Giữ cảnh báo rủi ro ngắn gọn ở cuối nếu cần.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)
MODEL3_RISK = step(
    "kiro", "Kiro Risk & Viewpoint", "Risk manager",
    "Kiro viết Rủi ro và quan điểm; kiểm soát dữ liệu thiếu/cũ, manual review; giọng dứt khoát.", "Codex Follow-up Plan",
    "Bạn là Kiro Risk Manager trong TradingAgents research.\n"
    "Kiểm tra toàn bộ phân tích và đưa khung rủi ro:\n"
    "- Data validation: giá/volume/news/indicator có mới không, nguồn nào cũ, cần manual review không.\n"
    "- Risk score 1-5 và lý do.\n"
    "- Position stance: Avoid / Watch / Small exploratory / Wait breakout / Wait pullback, kèm điều kiện xác nhận rõ.\n"
    "- Trade plan theo chiến lược LH nếu có entry/stop/takeprofit: vùng theo dõi, điều kiện kích hoạt, stop invalidation.\n"
    "- Checklist trước khi hành động.\n"
    "Viết giọng dứt khoát theo dữ liệu; tránh các câu rào kiểu 'chỉ tham khảo'. Giữ cảnh báo trách nhiệm/rủi ro ngắn gọn ở cuối nếu cần.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)
MODEL3_FOLLOWUP_PLAN = step(
    "chatgpt", "Codex Follow-up Plan", "Follow-up plan analyst",
    "Codex viết Kế hoạch theo dõi: dữ liệu cần refresh, trigger, lịch kiểm tra, điều kiện hành động.", "Word template",
    "Bạn là Codex. Viết PHẦN 8 — KẾ HOẠCH THEO DÕI cho báo cáo Super_LH.\n"
    "Gồm: dữ liệu cần refresh, chỉ báo cần theo dõi, catalyst/news cần theo dõi, trigger xác nhận/phủ định, checklist hành động. Không bịa số liệu.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)

MODEL3_HTML = step(
    "kiro", "Kiro Trading Dashboard HTML", "Frontend HTML dashboard",
    "Tạo dashboard/report HTML đẹp, rõ, tiếng Việt có dấu, gom News + Impact + Technical + Macro.", "Codex HTML/Data Test",
    "Tạo một file HTML hoàn chỉnh từ toàn bộ phân tích Model 3. Chỉ trả mã HTML từ <html> đến </html>, CSS inline.\n"
    "Bố cục bắt buộc theo TradingAgents research:\n"
    "- Header: mã cổ phiếu/công ty, ngày lập report, nguồn dữ liệu, data freshness.\n"
    "- Market snapshot: giá/volume/change/market overview nếu có.\n"
    "- Tin mới nhất từ RSS CafeF/Vietstock + cache fallback.\n"
    "- News & sentiment impact: mỗi tin 1 dòng Tích cực/Tiêu cực/Trung tính + sentiment tổng thể.\n"
    "- LH technical strategy: bảng từng chỉ báo RSI, MACD, volume, ROC, Ichimoku, Bollinger, RS support/resistance, rankScore, entry/stop/takeprofit; mỗi chỉ báo có nhãn Tích cực/Tiêu cực/Trung tính.\n"
    "- Fundamental & valuation: driver, KQKD/triển vọng, P/E/P/B/upside nếu có, data gaps.\n"
    "- Macro/ngành: các yếu tố hỗ trợ/rủi ro.\n"
    "- Bull case vs Bear case, catalysts, invalidation.\n"
    "- Risk manager & trade plan: stance, risk score, checklist, manual review.\n"
    "- Kết luận: hành động theo trigger đã xác nhận; giữ cảnh báo rủi ro ngắn gọn, không dùng câu rào kiểu 'chỉ tham khảo'.\n"
    "Tiếng Việt có dấu, không mojibake, không bịa số liệu.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)
MODEL3_VIETNAMESE_REPORT = step(
    "kiro", "Kiro Vietnamese Report Writer", "Vietnamese report writer",
    "Viết lại output phân tích của Codex thành tiếng Việt có dấu chuẩn, giữ nguyên dữ liệu/số liệu/logic; không phân tích thay Codex.", "Word template",
    "Bạn là Kiro Vietnamese Report Writer cho Model 3. Nhiệm vụ của bạn KHÔNG phải phân tích mới, mà là viết lại bản phân tích của Codex thành tiếng Việt có dấu chuẩn UTF-8.\n"
    "Quy tắc bắt buộc:\n"
    "- Giữ nguyên vai trò Codex là nguồn phân tích TA/research; bạn chỉ làm sạch văn phong/encoding.\n"
    "- Giữ nguyên số liệu, ngày, mã cổ phiếu, vùng giá, chỉ báo, bảng, nhãn Tích cực/Tiêu cực/Trung tính, stance, risk score.\n"
    "- Không thêm dữ liệu mới, không bịa, không xóa cảnh báo thiếu dữ liệu.\n"
    "- Sửa toàn bộ mất dấu/mojibake: ví dụ 'Tm tt' -> 'Tóm tắt', 'Ngn hng' -> 'Ngân hàng', 'c phiu' -> 'cổ phiếu'.\n"
    "- KHÔNG giữ nguyên cụm mất dấu. Nếu thấy câu bị mất dấu nhiều, hãy viết lại câu tự nhiên bằng tiếng Việt có dấu từ facts/số liệu, thay vì cố sửa từng chữ.\n"
    "- Chỉ cần giữ các facts quan trọng: mã, giá, ngày, chỉ báo, vùng hỗ trợ/kháng cự, stance, risk score, luận điểm bull/bear. Có thể rút gọn văn phong nhưng không đổi số liệu/logic.\n"
    "- Trả ra report Markdown hoàn chỉnh, không giải thích quá trình sửa.\n\n"
    "Nhiệm vụ gốc:\n{task}\n\nBản Codex/facts cần viết lại:\n{context}"
)

MODEL3_TEST = step(
    "chatgpt", "Codex HTML/Data Test", "Tester HTML/data",
    "Kiểm HTML, dữ liệu, nguồn tin, section kỹ thuật/vĩ mô, tiếng Việt có dấu.", "Claude hoặc người dùng",
    "Kiểm HTML/report Model 3:\n"
    "- Có đủ các phần TradingAgents: market snapshot, tin mới, tác động/sentiment, LH technical strategy, fundamental/valuation, macro/ngành, bull/bear, risk manager/trade plan, kết luận.\n"
    "- Mỗi tin có đánh giá Tích cực/Tiêu cực/Trung tính 1 dòng.\n"
    "- Không bịa số liệu/nguồn; thiếu dữ liệu phải có cảnh báo.\n"
    "- HTML hợp lệ, tiếng Việt có dấu, không mojibake.\n"
    "Nêu PASS/FAIL và bản sửa nếu cần.\n\n"
    "Nhiệm vụ:\n{task}\n\nBối cảnh:\n{context}"
)


class MSProviderAgent:
    def __init__(self, s: AgentStep):
        self.step = s
        self.id = s.agent_id + "-" + re.sub(r"[^a-z0-9]+", "-", s.label.lower()).strip("-")
        self.name = s.label
        self.description = s.goal

    async def run(self, messages=None, *, stream=False, session=None, **kwargs):  # noqa: ANN001
        text = get_text_agent(self.step.agent_id).complete(str(messages or ""), system=self.step.role)
        return AgentResponse(messages=[], value=text, response_id=f"resp-{int(time.time()*1000)}") if AgentResponse else text

    def create_session(self, *, session_id: str | None = None):
        return AgentSession(session_id=session_id) if AgentSession else None

    def get_session(self, service_session_id: str, *, session_id: str | None = None):
        return AgentSession(service_session_id=service_session_id, session_id=session_id) if AgentSession else None


def _installed(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _has_flag(task: str, flag: str) -> bool:
    return re.search(rf"(^|\s){re.escape(flag)}(\s|$)", task, flags=re.I) is not None


def _strip_command(task: str, names: str) -> str:
    task = re.sub(rf"^({names})(?:@[A-Za-z0-9_]+)?\s*[:：-]?\s*", "", task, flags=re.I).strip()
    task = re.sub(r"^(premium|full|grok)\s+", "", task, flags=re.I).strip()
    return task


def is_model2_task(task: str) -> bool:
    return task.strip().lower().startswith(("/model2", "model2:", "model 2:", "debate:", "tranh luận:", "tranh luan:"))


def is_model3_task(task: str) -> bool:
    return task.strip().lower().startswith(("/model3", "model3:", "model 3:", "tradingagents:", "trading agents:"))


def _clip(text: str, limit: int = 1800) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def _repair_mojibake(text: str) -> str:
    return repair_vietnamese_text(text)


def _extract_marked_result(text: str) -> str:
    if not text:
        return text
    # Grok terminal bridge may return clean FINAL_RESULT text, but Grok sometimes
    # still echoes/duplicates the user's START_RESULT marker inside the answer.
    # Prefer the last complete marker pair; if END_RESULT is missing, keep only
    # the tail after the last START_RESULT so noisy prompt/search text is dropped.
    matches = list(re.finditer(r"START_RESULT\s*(.*?)\s*END_RESULT", text, flags=re.I | re.S))
    if matches:
        return repair_vietnamese_text(matches[-1].group(1).strip())
    starts = list(re.finditer(r"START_RESULT", text, flags=re.I))
    if starts:
        return repair_vietnamese_text(text[starts[-1].end():].strip())
    return repair_vietnamese_text(text)


def _quality_score(text: str) -> int:
    q = vietnamese_quality_report(text)
    return int(q.get("mojibake_markers", 0)) * 10 + int(q.get("unaccented_markers", 0)) + int(q.get("replacement_chars", 0)) * 20


def _restore_vietnamese_with_ai(content: str, label: str, progress: ProgressFn) -> str:
    """Last-mile repair when a provider returns no-accent Vietnamese.

    Try stronger language agents and keep the best quality score. Do not add a
    separate timeout: Hòa Đại ka explicitly prefers quality over speed.
    """
    baseline = repair_vietnamese_text(content)
    before = vietnamese_quality_report(baseline)
    if not before.get("needs_repair"):
        return baseline
    progress(f"⚠️ {label}: phát hiện lỗi UTF-8/mất dấu {before}; chạy quality restore đa-agent trước khi ghi Word.")
    prompt = (
        "Phục hồi tiếng Việt có dấu và sửa mojibake cho văn bản báo cáo dưới đây.\n"
        "Yêu cầu nghiêm ngặt:\n"
        "- Chỉ sửa dấu/encoding/chính tả tiếng Việt bị mất dấu.\n"
        "- Giữ nguyên số liệu, mã cổ phiếu, giá, ngày, link, bảng markdown, thứ tự mục và ý nghĩa.\n"
        "- Không thêm dữ liệu mới, không rút gọn, không bình luận ngoài văn bản đã sửa.\n"
        "- Nếu một từ không thể khôi phục chắc chắn, giữ nguyên thay vì đoán sai.\n\n"
        "VĂN BẢN CẦN SỬA:\n" + baseline
    )
    best = baseline
    best_q = vietnamese_quality_report(best)
    # Chỉ dùng Kiro để restore/rewrite tiếng Việt; Codex vẫn giữ vai trò TA research.
    for agent in ("kiro",):
        try:
            fixed = _complete(agent, f"{agent.upper()} UTF-8 restore for {label}", prompt, "Bạn là bộ sửa UTF-8 tiếng Việt chuyên nghiệp. Chỉ trả lại văn bản đã sửa dấu, không thêm lời giải thích.", progress)
            fixed = repair_vietnamese_text(fixed)
            q = vietnamese_quality_report(fixed)
            if _quality_score(fixed) < _quality_score(best):
                best, best_q = fixed, q
                progress(f"✅ {label}: {agent} restore cải thiện chất lượng {before} -> {q}.")
            if not q.get("needs_repair"):
                return best
        except Exception as exc:  # noqa: BLE001
            progress(f"⚠️ {label}: {agent} UTF-8 restore lỗi {type(exc).__name__}: {exc}; thử agent khác.")
    if best_q.get("needs_repair"):
        progress(f"⚠️ {label}: đã restore đa-agent nhưng vẫn còn dấu hiệu lỗi {best_q}; giữ bản tốt nhất và report sẽ bị quality-gate cảnh báo.")
    return best


def _rewrite_codex_report_with_kiro(task: str, label: str, content: str, progress: ProgressFn, mode: str) -> str:
    """Keep Codex as analyst, use Kiro only as Vietnamese report writer."""
    progress(f"📝 {label}: Codex analysis bị lỗi tiếng Việt; giữ facts của Codex và gọi Kiro viết lại bản tiếng Việt sạch.")
    try:
        post = _run_step(task, MODEL3_VIETNAMESE_REPORT, [content], progress, 1, 1, mode)
        rewritten = repair_vietnamese_text(str(post.get("content", "")))
        if _quality_score(rewritten) < _quality_score(content):
            progress(f"✅ {label}: Kiro writer đã cải thiện quality {vietnamese_quality_report(content)} -> {vietnamese_quality_report(rewritten)}")
            return rewritten
    except Exception as exc:  # noqa: BLE001
        progress(f"⚠️ {label}: Kiro Vietnamese writer lỗi {type(exc).__name__}: {exc}; giữ bản Codex cleaned.")
    return repair_vietnamese_text(content)


def _rerun_step_for_quality(task: str, original: AgentStep, transcript: list[str], progress: ProgressFn, mode: str, bad_content: str) -> str:
    """If provider output is too corrupted, repair without changing Codex's analytical role.

    Codex remains the TA/research source. For Codex outputs, Kiro may rewrite only
    the Vietnamese wording/encoding from Codex facts. For non-Codex outputs, retry
    through Kiro as a fallback; Model3 does not call Gemini here.
    """
    best = repair_vietnamese_text(bad_content)
    best_q = vietnamese_quality_report(best)
    if not best_q.get("needs_repair"):
        return best
    if original.agent_id == "chatgpt":
        return _rewrite_codex_report_with_kiro(task, original.label, best, progress, mode)
    retry_agents = [a for a in ("kiro",) if a != original.agent_id]
    for agent in retry_agents:
        retry_step = AgentStep(agent, f"{original.label} UTF8 retry via {agent}", original.role, original.goal, original.speak_to, original.task_template)
        progress(f"🔁 {original.label}: output vẫn lỗi tiếng Việt {best_q}; chạy lại toàn bộ nhánh bằng {agent} để ưu tiên chất lượng.")
        try:
            prompt = retry_step.task_template.format(task=task, context="\n\n".join(transcript[-8:]))
            candidate = _complete(agent, retry_step.label, prompt, _system(retry_step), progress)
            candidate = _restore_vietnamese_with_ai(candidate, retry_step.label, progress)
            q = vietnamese_quality_report(candidate)
            if _quality_score(candidate) < _quality_score(best):
                best, best_q = candidate, q
                progress(f"✅ {original.label}: bản retry {agent} tốt hơn, quality {q}.")
            if not q.get("needs_repair"):
                return best
        except Exception as exc:  # noqa: BLE001
            progress(f"⚠️ {original.label}: retry {agent} lỗi {type(exc).__name__}: {exc}; thử agent khác.")
    return best


def _system(s: AgentStep) -> str:
    return f"Vai trò: {s.role}. Mục tiêu: {s.goal}. Bắt buộc trả lời tiếng Việt CÓ DẤU đầy đủ, UTF-8 chuẩn, không mojibake, không bỏ dấu. Nếu không thể giữ dấu tiếng Việt thì trả lỗi rõ, không xuất văn bản mất dấu. Bám dữ kiện, không bịa."


def _complete(agent_id: str, label: str, prompt: str, system: str, progress: ProgressFn) -> str:
    future = _EXECUTOR.submit(get_text_agent(agent_id).complete, prompt, system)
    started = time.time()
    next_tick = AGENT_TICK_SECONDS
    warned = False
    while True:
        try:
            return future.result(timeout=AGENT_TICK_SECONDS if AGENT_TIMEOUT_SECONDS <= 0 else min(AGENT_TICK_SECONDS, max(1, AGENT_TIMEOUT_SECONDS - int(time.time() - started))))
        except concurrent.futures.TimeoutError as exc:
            elapsed = int(time.time() - started)
            if AGENT_TIMEOUT_SECONDS > 0 and elapsed >= AGENT_TIMEOUT_SECONDS:
                future.cancel()
                raise TimeoutError(f"{agent_id} quá {AGENT_TIMEOUT_SECONDS}s chưa trả lời") from exc
            if elapsed >= next_tick:
                if elapsed >= AGENT_STUCK_WARN_SECONDS and not warned:
                    progress(f"⚠️ {label} đã chạy {elapsed}s, có thể đang suy nghĩ lâu hoặc provider đứng. Em vẫn chờ, không hủy.")
                    warned = True
                else:
                    progress(f"⏱️ {label} vẫn đang chờ response… {elapsed}s elapsed")
                next_tick += AGENT_TICK_SECONDS


def _model3_codex_fallback(task: str, s: AgentStep, exc: Exception) -> str:
    """Deterministic fallback for Model3 Codex sections when the LLM provider times out.

    The report must keep running for Hòa Đại ka. This fallback does not invent exact
    indicator values; the DOCX formatter still has the raw LHInvestment context/cache.
    """
    ticker_match = re.search(r"\b[A-Z]{2,5}\b", task.upper())
    ticker = ticker_match.group(0) if ticker_match else "MÃ CP"
    reason = f"{type(exc).__name__}: {str(exc)[:240]}"
    if s in (MODEL3_ANALYSIS,):
        return (
            f"## LHINVESTMENT INDICATOR MATRIX — {ticker}\n"
            f"Provider Codex bị timeout nên dùng fallback an toàn từ context nội bộ.\n\n"
            "### Cặp 1 — Xu hướng / MA\n"
            "Đọc trực tiếp các trường giá EOD, MA10/20/50/100/200 và cấu trúc xu hướng trong bảng dữ liệu LHInvestment. "
            "Nếu giá nằm trên các MA ngắn và trung hạn thì ưu tiên xu hướng tích cực; nếu dưới MA20/50 thì giảm tỷ trọng theo kỷ luật.\n\n"
            "### Cặp 2 — Động lượng\n"
            "RSI, MACD, MACD signal/histogram và ROC/ret5 được dùng để xác nhận xung lực. "
            "Không suy diễn số liệu; số cụ thể lấy từ context/bảng raw khi xuất báo cáo.\n\n"
            "### Cặp 3 — Sức mạnh xu hướng / dòng tiền\n"
            "ADX, +DI/-DI, volume, avgVol20 và volumeRatio là nhóm xác nhận chất lượng nhịp tăng/giảm. "
            "Volume cao hơn trung bình 20 phiên mới được coi là xác nhận dòng tiền.\n\n"
            "### Cặp 4 — Vùng giá / rủi ro\n"
            "Dùng Bollinger, Ichimoku, hỗ trợ/kháng cự, RS levels, stop/invalid để lập vùng theo dõi. "
            "Không khuyến nghị mua đuổi nếu giá sát kháng cự hoặc rủi ro invalid cao.\n\n"
            f"Ghi chú kỹ thuật: Codex timeout ({reason}); workflow tiếp tục để không mất báo cáo."
        )
    if s in (MODEL3_FUNDAMENTAL, MODEL3_BULL_BEAR, MODEL3_FOLLOWUP_PLAN):
        if s is MODEL3_FUNDAMENTAL or s.label == MODEL3_FUNDAMENTAL.label:
            title = "Fundamental & Macro"
        elif s is MODEL3_BULL_BEAR or s.label == MODEL3_BULL_BEAR.label:
            title = "Bull / Bear / Catalyst"
        elif s is MODEL3_FOLLOWUP_PLAN or s.label == MODEL3_FOLLOWUP_PLAN.label:
            title = "Kế hoạch theo dõi"
        else:
            title = s.label
        return (
            f"## {title} — {ticker}\n"
            f"Provider Codex bị timeout nên dùng fallback an toàn, không bịa dữ liệu.\n\n"
            "- Chỉ sử dụng số liệu đã có trong context LHInvestment / macro / report cache khi formatter xuất DOCX.\n"
            "- Nếu thiếu dữ liệu định lượng, đánh dấu cần kiểm chứng thay vì tự điền.\n"
            "- Ưu tiên quản trị rủi ro: xác định vùng invalid, catalyst cần theo dõi, và điều kiện thay đổi quan điểm.\n"
            "- Báo cáo vẫn chạy tiếp để Word/NotebookLM có file kiểm thử.\n\n"
            f"Ghi chú kỹ thuật: Codex timeout ({reason})."
        )
    raise exc


def _run_step(task: str, s: AgentStep, transcript: list[str], progress: ProgressFn, idx: int, total: int, mode: str) -> dict[str, Any]:
    progress(f"⏳ [{idx}/{total}] {s.label}: {s.goal}")
    started = time.time()
    prompt = s.task_template.format(task=task, context="\n\n".join(transcript[-8:]))
    try:
        content = _repair_mojibake(_complete(s.agent_id, s.label, prompt, _system(s), progress))
    except Exception as exc:
        if s in (MODEL3_ANALYSIS, MODEL3_FUNDAMENTAL, MODEL3_BULL_BEAR, MODEL3_FOLLOWUP_PLAN):
            progress(f"⚠️ {s.label}: provider lỗi/timeout, dùng fallback nội bộ để workflow không chết ({type(exc).__name__}).")
            content = _model3_codex_fallback(task, s, exc)
        else:
            raise
    # UTF-8 skill: clean at provider boundary first. Do not push obviously broken
    # Vietnamese directly into DOCX/frontend, and avoid long full-text restore loops.
    if has_vietnamese_quality_issue(content):
        progress(f"🧹 {s.label}: lọc UTF-8 rule-based trước khi xét rewrite/restore: {vietnamese_quality_report(content)}")
        content = repair_vietnamese_text(content)
    if has_vietnamese_quality_issue(content) and s.label == MODEL3_TEST.label:
        progress(f"⚠️ {s.label}: còn lỗi tiếng Việt sau cleaner {vietnamese_quality_report(content)}; bỏ restore dài cho bước test phụ, giữ bản cleaned để tránh chậm pipeline.")
    elif has_vietnamese_quality_issue(content) and s.label != MODEL3_VIETNAMESE_REPORT.label:
        # Fan-out mode must finish. Do not spawn nested repair agents here; rule-based cleaner + DOCX cleaner handle common glitches.
        progress(f"⚠️ {s.label}: còn dấu hiệu UTF-8 sau cleaner {vietnamese_quality_report(content)}; bỏ nested restore để tránh nghẽn, tiếp tục xuất báo cáo.")
    elapsed = time.time() - started
    progress(f"✅ {s.label} xong ({elapsed:.1f}s)")
    return {"agent": s.agent_id, "name": s.label, "action": s.role, "content": content, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "elapsed": elapsed, "speaks_to": s.speak_to, "framework": mode}


def _append(state: dict[str, Any], transcript: list[str], post: dict[str, Any]) -> None:
    post["id"] = len(state["feed"]) + 1
    state["feed"].append(post)
    transcript.append(f"## {post['name']}\n{_clip(post.get('content',''))}")


def _err(s: AgentStep, exc: Exception, elapsed: float, mode: str) -> dict[str, Any]:
    return {"agent": s.agent_id, "name": s.label, "action": "LỖI", "content": f"Agent lỗi sau {elapsed:.1f}s: {type(exc).__name__}: {exc}. Workflow ghi lỗi và chạy tiếp.", "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "elapsed": elapsed, "speaks_to": s.speak_to, "framework": mode}


def _create_crewai(steps: list[AgentStep], progress: ProgressFn) -> None:
    if CrewAIAgent is None or CrewAITask is None:
        progress("⚠️ CrewAI import lỗi, workflow vẫn chạy qua provider nội bộ.")
        return
    try:
        agents = [CrewAIAgent(role=s.role, goal=s.goal, backstory=f"{s.label}. Luôn trả tiếng Việt có dấu.", verbose=False, allow_delegation=False) for s in steps]
        tasks = [CrewAITask(description=s.task_template, expected_output="Kết quả tiếng Việt có dấu, đầy đủ, không mojibake.", agent=a) for s, a in zip(steps, agents)]
        if CrewAICrew is not None:
            _ = CrewAICrew(agents=agents, tasks=tasks, verbose=False)
        progress(f"✅ CrewAI native objects đã tạo: {len(agents)} agents, {len(tasks)} tasks")
    except Exception as exc:  # noqa: BLE001
        progress(f"⚠️ CrewAI object init lỗi ({type(exc).__name__}); workflow vẫn chạy bằng provider nội bộ.")


def _create_ms(steps: list[AgentStep], progress: ProgressFn) -> None:
    if GroupChatBuilder is None:
        progress("⚠️ MS Agent Framework import lỗi, workflow vẫn chạy qua provider nội bộ.")
        return
    try:
        _ = GroupChatBuilder(participants=[MSProviderAgent(s) for s in steps])
        progress(f"✅ MS Agent Framework GroupChatBuilder đã tạo: {len(steps)} participants")
    except Exception as exc:  # noqa: BLE001
        progress(f"⚠️ MS Agent Framework init lỗi ({type(exc).__name__}); workflow vẫn chạy bằng provider nội bộ.")


def _run_sequence(task: str, steps: list[AgentStep], progress: ProgressFn, mode: str, state: dict[str, Any] | None = None, transcript: list[str] | None = None) -> dict[str, Any]:
    state = state or {"task": task, "feed": [], "framework": mode}
    state["task"] = task
    transcript = transcript or []
    for idx, s in enumerate(steps, 1):
        started = time.time()
        try:
            post = _run_step(task, s, transcript, progress, idx, len(steps), mode)
        except Exception as exc:  # noqa: BLE001
            post = _err(s, exc, time.time() - started, mode)
            progress(f"❌ {s.label} lỗi ({type(exc).__name__})")
        _append(state, transcript, post)
    return state


def run_main_workflow(task: str, progress: ProgressFn) -> dict[str, Any]:
    premium = _has_flag(task, "premium")
    task = _strip_command(task, r"/model1|model1|model 1|suite")
    mode = "Model 1 - CrewAI optimized" + (" premium" if premium else "")
    progress(f"🧩 {mode}: CrewAI={'OK' if _installed('crewai') else 'MISSING'}")
    opening = [CLAUDE_BRAINSTORM, KIRO_DISPATCH] if premium else [KIRO_DISPATCH]
    final_steps = [CODEX_TEST, CLAUDE_FINAL] if premium else [CODEX_TEST]
    all_steps = opening + [CODEX_HARD, KIRO_FRONTEND] + final_steps
    _create_crewai(all_steps, progress)
    state: dict[str, Any] = {"task": task, "feed": [], "framework": mode}
    transcript: list[str] = []
    total = len(opening) + 1 + len(final_steps)
    for idx, s in enumerate(opening, 1):
        started = time.time()
        try: post = _run_step(task, s, transcript, progress, idx, total, mode)
        except Exception as exc: post = _err(s, exc, time.time() - started, mode); progress(f"❌ {s.label} lỗi ({type(exc).__name__})")
        _append(state, transcript, post)
    progress("🚦 Chạy song song: Codex Hard Analysis + Kiro Frontend/Checklist")
    context = list(transcript)
    futures = {_EXECUTOR.submit(lambda x=s: _run_step(task, x, context, progress, len(opening)+1, total, mode)): (s, time.time()) for s in [CODEX_HARD, KIRO_FRONTEND]}
    for fut in concurrent.futures.as_completed(futures):
        s, started = futures[fut]
        try: post = fut.result()
        except Exception as exc: post = _err(s, exc, time.time() - started, mode); progress(f"❌ {s.label} lỗi ({type(exc).__name__})")
        _append(state, transcript, post)
    for j, s in enumerate(final_steps, len(opening)+2):
        started = time.time()
        try: post = _run_step(task, s, transcript, progress, j, total, mode)
        except Exception as exc: post = _err(s, exc, time.time() - started, mode); progress(f"❌ {s.label} lỗi ({type(exc).__name__})")
        _append(state, transcript, post)
    return state


def run_debate_workflow(task: str, progress: ProgressFn) -> dict[str, Any]:
    full = _has_flag(task, "full")
    with_grok = _has_flag(task, "grok") or full
    task = _strip_command(task, r"/model2|model2|model 2|debate|tranh luận|tranh luan")
    mode = "Model 2 - MS Agent debate" + (" full" if full else " compact") + (" + Grok" if with_grok else "")
    progress(f"🧩 {mode}: MS Agent Framework={'OK' if _installed('agent_framework_orchestrations') else 'MISSING'}")
    steps = (MODEL2_FULL_BASE + ([GROK_VIEW] if with_grok else []) + [KIRO_JUDGE, CLAUDE_DEBATE_FINAL]) if (full or with_grok) else MODEL2_COMPACT
    _create_ms(steps, progress)
    return _run_sequence(task, steps, progress, mode)


def _write_html(task: str, html: str) -> str:
    out = Path("outputs") / "model3"
    out.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", task.strip())[:50].strip("-") or "tradingagents-report"
    path = out / f"{time.strftime('%Y%m%d-%H%M%S')}-{safe}.html"
    if "<html" not in html.lower():
        html = "<!doctype html><html lang='vi'><head><meta charset='utf-8'><title>Model 3 Report</title></head><body><pre>" + html.replace("<", "&lt;") + "</pre></body></html>"
    path.write_text(html, encoding="utf-8")
    return str(path)


def _write_docx(task: str, state: dict[str, Any]) -> str:
    out = Path("outputs") / "model3"
    out.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "-", task.strip())[:50].strip("-") or "tradingagents-report"
    path = out / f"{time.strftime('%Y%m%d-%H%M%S')}-{safe}.docx"
    return write_model3_docx(task, state, path)


STOCK_ALIASES = {
    "VPB": ["VPB", "VPBank", "Ngân hàng TMCP Việt Nam Thịnh Vượng"],
    "TCB": ["TCB", "Techcombank", "Ngân hàng TMCP Kỹ thương Việt Nam"],
    "SSI": ["SSI", "Chứng khoán SSI", "Công ty Cổ phần Chứng khoán SSI", "SSI Securities"],
    "MWG": ["MWG", "Thế Giới Di Động", "Mobile World", "CTCP Đầu tư Thế Giới Di Động", "Điện Máy Xanh", "Bách Hóa Xanh"],
}

DIRECT_NEWS_KEYWORDS = (
    "lợi nhuận", "lntt", "kqkd", "doanh thu", "eps", "roe", "roa", "biên lợi nhuận",
    "kế hoạch", "mục tiêu", "triển vọng", "dự báo", "định giá", "target", "khuyến nghị",
    "cổ tức", "phát hành", "tăng vốn", "esop", "mua lại cổ phiếu", "room ngoại",
    "đại hội cổ đông", "đhđcđ", "ban lãnh đạo", "bổ nhiệm", "miễn nhiệm",
    "m&a", "sáp nhập", "thoái vốn", "đầu tư", "hợp tác", "đối tác",
    "pháp lý", "thanh tra", "xử phạt", "kiện", "trái phiếu", "nợ", "nợ xấu",
    "nim", "tín dụng", "casa", "margin", "tự doanh", "môi giới", "thị phần",
    "chuỗi", "cửa hàng", "bách hóa xanh", "điện máy xanh", "tài sản số",
)

MARKET_ONLY_KEYWORDS = (
    "vn-index", "vnindex", "hvnx-index", "hơn 1.600 điểm", "thị trường chứng khoán",
    "cổ phiếu nào", "nhóm cổ phiếu", "top cổ phiếu", "dòng tiền", "khối ngoại",
    "chứng khoán hôm nay", "nhận định thị trường", "thị trường chung", "cổ phiếu ngân hàng đồng loạt",
    "chứng quyền", "covered warrant", "cw.", "cổ phiếu đáng chú ý", "lọt rổ", "etf",
)


def _extract_ticker(text: str) -> str:
    t = (text or "").upper()
    for sym, aliases in STOCK_ALIASES.items():
        if sym in t or any(a.upper() in t for a in aliases):
            return sym
    skip = {"TIN", "TUC", "TỨC", "KIRO", "CODEX", "BOT", "HTML", "WORD", "DOCX", "TRUC", "TIẾP", "TRỰC"}
    for m in re.findall(r"\b[A-Z]{3,5}\b", t):
        if m not in skip:
            return m
    return ""


def _unwrap_url(url: str) -> str:
    if not url:
        return url
    u = url.replace("&amp;", "&")
    if u.startswith("//"):
        u = "https:" + u
    try:
        qs = parse_qs(urlparse(u).query)
        if qs.get("uddg"):
            return unquote(qs["uddg"][0])
    except Exception:
        pass
    return u


def _source_from_url(url: str) -> str:
    try:
        return urlparse(_unwrap_url(url)).netloc.lower().replace("www.", "") or "web"
    except Exception:
        return "web"


def _norm_title(title: str) -> str:
    s = re.sub(r"\s+[-–—]\s+[^-–—|]+$", "", title or "")
    s = re.sub(r"[^\w\sÀ-ỹ]", " ", s.lower(), flags=re.UNICODE)
    return re.sub(r"\s+", " ", s).strip()


def _add_unique_news(items: list[dict[str, str]], item: dict[str, str], per_domain_limit: int = 3) -> None:
    nt = _norm_title(item.get("title", ""))
    if not nt:
        return
    item["link"] = _unwrap_url(item.get("link", ""))
    item["source"] = _source_from_url(item.get("link", ""))
    if any(_norm_title(x.get("title", "")) == nt for x in items):
        return
    if sum(1 for x in items if x.get("source") == item.get("source")) >= per_domain_limit:
        return
    items.append(item)


def _build_news_queries(task: str) -> list[str]:
    sym = _extract_ticker(task)
    if sym:
        aliases = STOCK_ALIASES.get(sym, [sym])
        main = " OR ".join(f'"{a}"' if " " in a else a for a in aliases)
        return [
            f'({main}) 2026 lợi nhuận KQKD kế hoạch cổ tức tăng vốn',
            f'({main}) 2026 triển vọng tăng trưởng định giá khuyến nghị target',
            f'({main}) 2026 đại hội cổ đông ĐHĐCĐ phát hành ESOP cổ tức',
            f'({main}) 2026 rủi ro pháp lý nợ xấu thanh tra trái phiếu',
            f'({main}) 2026 CafeF Vietstock 24HMoney FireAnt Stockbiz Mekong ASEAN',
            f'({main}) site:cafef.vn 2026',
            f'({main}) site:vietstock.vn 2026',
            f'({main}) site:24hmoney.vn 2026',
            f'({main}) site:fireant.vn 2026',
            f'({main}) site:mekongasean.vn 2026',
        ]
    return [task, f"{task} 2026"]


def _parse_news_date(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(value).date().isoformat()
    except Exception:
        m = re.search(r"20\d{2}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]20\d{2}", value)
        return m.group(0) if m else value


def _news_hay(item: dict[str, str]) -> str:
    return " ".join(str(item.get(k, "")) for k in ("title", "snippet", "summary", "description", "source"))


def _mentions_symbol(item: dict[str, str], symbol: str) -> bool:
    if not symbol:
        return True
    aliases = STOCK_ALIASES.get(symbol.upper(), [symbol.upper()])
    hay = _news_hay(item).upper()
    for alias in aliases:
        a = alias.upper()
        if re.search(rf"(?<![A-Z0-9]){re.escape(a)}(?![A-Z0-9])", hay) or a in hay:
            return True
    return False


def _has_direct_trigger(item: dict[str, str]) -> bool:
    hay = _news_hay(item).lower()
    return any(k in hay for k in DIRECT_NEWS_KEYWORDS)


def _is_wrong_company_news(item: dict[str, str], symbol: str) -> bool:
    hay = _news_hay(item).lower()
    if symbol.upper() == "FPT" and ("chứng khoán fpt" in hay or "fpts" in hay or "fpt securities" in hay):
        return True
    return False


def _is_market_only_news(item: dict[str, str], symbol: str = "") -> bool:
    hay = _news_hay(item).lower()
    title_raw = str(item.get("title", ""))
    title = title_raw.lower()
    if any(k in hay for k in MARKET_ONLY_KEYWORDS):
        return True
    # Titles that list many tickers are usually market/sector roundups, not direct-impact news.
    tickers = set(re.findall(r"\b[A-Z]{3}\b", title_raw))
    if symbol and symbol.upper() in tickers and len(tickers) >= 3:
        return True
    if len(tickers) >= 3 and not _has_direct_trigger(item):
        return True
    return False


def _direct_news_score(item: dict[str, str], symbol: str) -> int:
    hay = _news_hay(item).upper()
    title = str(item.get("title", "")).upper()
    score = 0
    if _mentions_symbol(item, symbol):
        score += 80
    aliases = STOCK_ALIASES.get(symbol.upper(), [symbol.upper()]) if symbol else []
    if any(a.upper() in title for a in aliases):
        score += 35
    if _has_direct_trigger(item):
        score += 50
    if re.search(r"LỢI NHUẬN|LNTT|KQKD|QUÝ|TĂNG TRƯỞNG|CỔ TỨC|PHÁT HÀNH|TĂNG VỐN|ESOP|ĐHĐCĐ|ĐẠI HỘI CỔ ĐÔNG|DỰ BÁO|KẾ HOẠCH|TARGET|KHUYẾN NGHỊ", hay):
        score += 35
    if _is_market_only_news(item, symbol) or _is_wrong_company_news(item, symbol):
        score -= 200
    return score


def _select_direct_news(items: list[dict[str, str]], symbol: str, limit: int = 12) -> list[dict[str, str]]:
    # Strict: must mention ticker/company AND have a direct business/corporate trigger.
    filtered = []
    for x in items:
        if symbol and not _mentions_symbol(x, symbol):
            continue
        if _is_wrong_company_news(x, symbol):
            continue
        if _is_market_only_news(x, symbol):
            continue
        if not _has_direct_trigger(x):
            continue
        filtered.append(x)
    filtered.sort(key=lambda x: (_direct_news_score(x, symbol), x.get("published", "")), reverse=True)
    out: list[dict[str, str]] = []
    for it in filtered:
        _add_unique_news(out, it, per_domain_limit=4)
        if len(out) >= limit:
            break
    return out


def _searxng_news(client: httpx.Client, query: str, limit: int) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    try:
        r = client.get(
            "http://localhost:8080/search",
            params={"format": "json", "q": query, "language": "vi", "categories": "news"},
            headers={"User-Agent": "Mozilla/5.0"},
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        return out
    for it in data.get("results", [])[: limit * 2]:
        title = re.sub(r"\s+", " ", str(it.get("title") or "")).strip()
        link = str(it.get("url") or it.get("link") or "").strip()
        snippet = re.sub(r"\s+", " ", str(it.get("content") or it.get("snippet") or "")).strip()
        published = str(it.get("publishedDate") or it.get("published") or "").strip()
        if title and link:
            _add_unique_news(out, {"title": title, "link": link, "published": _parse_news_date(published), "snippet": snippet[:500]})
        if len(out) >= limit:
            break
    return out


def _duckduckgo_news(client: httpx.Client, query: str, limit: int) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    r = client.get(f"https://duckduckgo.com/html/?q={quote_plus(query)}", headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    pattern = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.I | re.S)
    for href, title_html in pattern.findall(r.text):
        title = re.sub(r"<[^>]+>", " ", title_html)
        title = re.sub(r"\s+", " ", title).strip()
        _add_unique_news(out, {"title": title, "link": href, "published": "", "snippet": ""})
        if len(out) >= limit:
            break
    return out


def _google_news(client: httpx.Client, query: str, limit: int) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=vi&gl=VN&ceid=VN:vi"
    r = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    root = ET.fromstring(r.content)
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = _parse_news_date(item.findtext("pubDate") or "")
        desc = re.sub(r"<[^>]+>", " ", item.findtext("description") or "")
        desc = re.sub(r"\s+", " ", desc).strip()
        _add_unique_news(out, {"title": title, "link": link, "published": pub, "snippet": desc[:500]})
        if len(out) >= limit:
            break
    return out


def _tradingagents_news_context(task: str, progress: ProgressFn, limit: int = 8) -> str:
    sym = _extract_ticker(task)
    if not sym:
        return "TRADINGAGENTS_NEWS_CONTEXT: Không xác định được ticker để gọi TradingAgents get_news."
    try:
        from tradingagents.agents.utils.news_data_tools import get_news
    except Exception as exc:  # noqa: BLE001
        return f"TRADINGAGENTS_NEWS_CONTEXT_ERROR: import get_news lỗi {type(exc).__name__}: {exc}"
    # Hòa Đại ka muốn tin trong năm 2026; dùng TradingAgents tool trước, nếu vendor thiếu coverage thì vẫn ghi rõ.
    try:
        progress(f"📰 TradingAgents News: gọi get_news({sym}, 2026-01-01, 2026-12-31)...")
        raw = get_news.func(sym, "2026-01-01", "2026-12-31")
    except Exception as exc:  # noqa: BLE001
        return f"TRADINGAGENTS_NEWS_CONTEXT_ERROR: get_news lỗi {type(exc).__name__}: {exc}"
    return "\n".join([
        "TRADINGAGENTS_NEWS_CONTEXT — dữ liệu từ TradingAgents get_news vendor hiện cấu hình.",
        "Ticker: " + sym,
        "Khoảng ngày: 2026-01-01 đến 2026-12-31",
        "Lưu ý: nếu vendor là yfinance/AlphaVantage không cover mã Việt Nam tốt thì kết quả có thể trống; dùng song song với web search VN.",
        "RAW TRADINGAGENTS NEWS:",
        _clip(str(raw), 5000),
    ])


def build_model3_news_context(task: str, progress: ProgressFn, limit: int = 12) -> str:
    queries = _build_news_queries(task)
    sym = _extract_ticker(task)
    items: list[dict[str, str]] = []
    ta_context = _tradingagents_news_context(task, progress)
    progress("🔎 Model 3: web search VN/public đang tìm tin trực tiếp song song cho Kiro News...")
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            searx_hits = 0
            for q in queries:
                try:
                    found = _searxng_news(client, q, limit)
                    searx_hits += len(found)
                    for it in found:
                        _add_unique_news(items, it, per_domain_limit=4)
                except Exception as exc:  # noqa: BLE001
                    progress(f"⚠️ SearXNG query lỗi: {type(exc).__name__}")
            if searx_hits:
                progress(f"🔎 Model 3: SearXNG skill search trả {searx_hits} kết quả thô; tiếp tục cross-check DuckDuckGo/Google News.")
            for q in queries:
                try:
                    for it in _duckduckgo_news(client, q, limit):
                        _add_unique_news(items, it, per_domain_limit=4)
                except Exception as exc:  # noqa: BLE001
                    progress(f"⚠️ DuckDuckGo query lỗi: {type(exc).__name__}")
            for q in queries:
                try:
                    for it in _google_news(client, q, limit):
                        _add_unique_news(items, it, per_domain_limit=4)
                except Exception as exc:  # noqa: BLE001
                    progress(f"⚠️ Google News query lỗi: {type(exc).__name__}")
    except Exception as exc:  # noqa: BLE001
        web_context = f"WEB_SEARCH_CONTEXT_ERROR: {type(exc).__name__}: {exc}"
        return ta_context + "\n\n" + web_context
    items = _select_direct_news(items, sym, limit=limit)
    lines = [
        ta_context,
        "",
        "WEB_SEARCH_CONTEXT — hệ thống tìm web công khai cho Kiro News.",
        "Prompt bắt buộc: Tìm kiếm 3-5 tin tức tiêu cực/tích cực khác nội dung liên quan TRỰC TIẾP đến cổ phiếu X trong năm 2026. Phân tích và đánh giá tác động tới cổ phiếu X.",
        "Truy vấn đã tối ưu: " + " | ".join(queries),
        "Đã lọc ưu tiên title/snippet có ticker/tên doanh nghiệp, lọc trùng tiêu đề và hạn chế lặp domain.",
        "",
        "RAW WEB RESULTS:",
    ]
    if not items:
        lines.append("Không tìm thấy kết quả web công khai đủ rõ sau khi lọc ticker trực tiếp.")
    for i, n in enumerate(items[:limit], 1):
        lines.append(f"{i}. [{n.get('published','')}] {n.get('title')} — {n.get('source','web')}\nURL: {n.get('link')}\nSnippet: {n.get('snippet','')}")
    return "\n".join(lines)


def _run_grok_news_cli(symbol: str, progress: ProgressFn, timeout: int = 600) -> str:
    """Run Grok news directly through the 9router OpenAI-compatible API.

    No Grok terminal/PTY/bridge is used here. The function keeps the same Model3
    news quality gate: Grok-sourced answer, direct 2026 news only, no silent web
    fallback, and fail loudly if the API/key/model is not usable.
    """
    def _load_local_env() -> None:
        env_paths = [
            Path(__file__).resolve().parent / ".env",
            Path(__file__).resolve().parents[3] / "OPENAI_KEY_INPUT.env",
        ]
        for env_path in env_paths:
            if not env_path.exists():
                continue
            for raw in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value and (not os.environ.get(key) or os.environ.get(key) == "sk-dummy-crewai-construction-only"):
                    os.environ[key] = value

    _load_local_env()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "sk-dummy-crewai-construction-only":
        raise RuntimeError("Grok 9router API thiếu OPENAI_API_KEY/keypoint API trong .env hoặc environment")
    # Use the existing keypoint/OpenAI-compatible API setup; this is a direct
    # HTTP API call, not the old Grok terminal/PTY bridge.
    base_url = (
        os.environ.get("GROK_9ROUTER_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or "https://api.9router.com/v1"
    ).rstrip("/")
    model = (
        os.environ.get("GROK_9ROUTER_MODEL")
        or os.environ.get("GROK_MODEL")
        or "Grok"
    ).strip()

    def _chat(prompt_text: str, call_timeout: int) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Bạn là Grok News Analyst cho cổ phiếu Việt Nam. Luôn trả lời tiếng Việt Unicode sạch, bám nguồn, không bịa."},
                {"role": "user", "content": prompt_text},
            ],
            "temperature": 0.2,
        }
        with httpx.Client(timeout=call_timeout) as client:
            resp = client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
        if resp.status_code >= 400:
            raise RuntimeError(f"Grok 9router API lỗi HTTP {resp.status_code}: {resp.text[-1200:]}")
        raw_text = resp.text.strip()
        try:
            data = resp.json()
        except Exception:
            # Some keypoint proxies return JSON plus `data: [DONE]`, or newline-
            # delimited JSON chunks. Decode the first/last choices object safely.
            data = None
            decoder = json.JSONDecoder()
            try:
                obj, _ = decoder.raw_decode(raw_text)
                if isinstance(obj, dict) and obj.get("choices"):
                    data = obj
            except Exception:
                pass
            if data is None:
                for line in raw_text.splitlines():
                    line = line.strip()
                    if not line or line == "[DONE]":
                        continue
                    if line.startswith("data:"):
                        line = line[5:].strip()
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if isinstance(obj, dict) and obj.get("choices"):
                        data = obj
            if data is None:
                raise RuntimeError(f"Grok 9router API trả non-JSON: {raw_text[-1200:]}")
        try:
            choice = data["choices"][0]
            msg = choice.get("message") or {}
            text = msg.get("content") or choice.get("text") or choice.get("delta", {}).get("content")
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Grok 9router API trả schema lạ: {json.dumps(data, ensure_ascii=False)[:1200]}") from exc
        return repair_vietnamese_text(str(text or "").strip())

    progress(f"🧠 Grok News: gọi trực tiếp 9router API, model={model}, base={base_url} (không dùng terminal)...")
    smoke_out = _chat("Return exactly: OK", min(60, timeout))
    try:
        out_dir = Path("outputs") / "model3"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{symbol}_grok_9router_smoke_stdout.txt").write_text(smoke_out, encoding="utf-8")
    except Exception:
        pass
    if "OK" not in smoke_out.upper():
        raise RuntimeError(f"Grok 9router preflight không trả OK; output={smoke_out[-500:]}")

    prompt = (
        f"Tìm web và trả lời tiếng Việt có dấu. Lấy tối đa 5 tin có NGÀY CÔNG BỐ NẰM TRONG NĂM 2026 liên quan TRỰC TIẾP cổ phiếu {symbol}. "
        "Ưu tiên KQKD, doanh thu/lợi nhuận, kế hoạch. "
        "CẤM lấy tin có ngày công bố năm 2025 hoặc trước đó, kể cả khi nội dung nói về kế hoạch 2026. "
        "Nếu nguồn có tiêu đề/nội dung nhắc KQKD quý IV/2025 nhưng ngày đăng là 2026 thì chỉ được dùng khi ghi rõ ngày đăng 2026; nếu không xác định được ngày đăng 2026 thì loại bỏ. "
        "Mỗi tin phải có Ngày công bố dạng dd/mm/2026 hoặc tháng/năm 2026, Nguồn/link, Tóm tắt, Tác động. "
        "Nếu không đủ 5 tin trực tiếp trong năm 2026 thì chỉ trả số tin tìm được và ghi rõ thiếu nguồn trực tiếp 2026. Không bịa, không dùng tin cũ để bù số lượng. "
        "Mỗi tin gồm 2 câu: tóm tắt 1 câu, đánh giá tác động cổ phiếu tăng/giảm/trung tính bao nhiêu % và vì sao. "
        "Bắt buộc tiếng Việt Unicode UTF-8 sạch, không viết không dấu, không mojibake. "
        "Trả kết quả theo từng tin có nhãn Ngày công bố, Tóm tắt và Tác động; kèm nguồn/link nếu có."
    )
    progress(f"🔎 Grok News: bắt đầu research tin trực tiếp cho {symbol} qua 9router API...")
    out = _chat(prompt, timeout)
    stale_pattern = re.compile(r"(?i)(tin\s+\d+[^\n]{0,120}(?:2025|2024|2023)|ngày\s+công\s+bố\s*[:\-]?\s*[^\n]{0,80}(?:2025|2024|2023)|\b(?:20/01/2026|21/01/2026)\b[^\n]{0,160}(?:quý\s*iv/2025|q4/2025)|\b2025\b[^\n]{0,80}(?:công\s+bố|ngày\s+đăng|nguồn))")
    if out and stale_pattern.search(out):
        progress("⚠️ Grok News: phát hiện dấu hiệu tin cũ/2025 trong output API; retry với bộ lọc chỉ tin công bố 2026...")
        retry_prompt = prompt + (
            "\n\nLẦN TRƯỚC CÓ TIN CŨ. Hãy tự kiểm tra lại: loại mọi Tin có ngày công bố không thuộc 2026. "
            "Không được đưa Tin 2025, không đưa tin quý IV/2025 nếu nguồn/ngày đăng không xác nhận trong năm 2026. "
            "Nếu còn nghi ngờ ngày đăng, bỏ tin đó."
        )
        retry_out = _chat(retry_prompt, timeout)
        if retry_out:
            out = retry_out
    try:
        out_dir = Path("outputs") / "model3"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{symbol}_grok_9router_news_stdout.txt").write_text(out, encoding="utf-8")
    except Exception:
        pass
    if not out or re.search(r"^\s*(ok|done)\s*$", out, re.I):
        raise RuntimeError("Grok 9router API không trả nội dung tin tức.")
    q = vietnamese_quality_report(out)
    if q.get("mojibake_markers") or q.get("replacement_chars"):
        raise RuntimeError(f"Grok 9router API trả output lỗi UTF-8/mojibake: {q}")
    return out



def run_model3_workflow(task: str, progress: ProgressFn) -> dict[str, Any]:
    premium = _has_flag(task, "premium")
    task = _strip_command(task, r"/model3|model3|model 3|tradingagents|trading agents")
    mode = "Model 3 - TradingAgents Word" + (" premium" if premium else "")
    progress(f"🧩 {mode}: tradingagents={'OK' if _installed('tradingagents') else 'MISSING'}")
    progress("📥 Super_LH: phân công mới — GrokX news-impact, Codex indicator/fundamental/bull-bear/follow-up, Kiro scenario/risk; executive summary viết cuối sau khi đủ dữ liệu…")
    lh_context = build_lhinvestment_context(task)
    news_context_future = _EXECUTOR.submit(build_model3_news_context, task, progress)

    state: dict[str, Any] = {"task": task, "feed": [], "framework": mode}
    transcript: list[str] = []
    base_context = task + "\n\n" + lh_context
    progress("🚦 Super_LH fan-out: chạy song song các phân tích chính trên cùng context ban đầu; executive summary sẽ chạy cuối để không tóm tắt khi chưa có dữ liệu.")

    def _run_news_branch() -> dict[str, Any]:
        # Build public-web context only for diagnostics/logging. Per Hòa Đại ka:
        # do NOT replace Grok news with web fallback in the investor report.
        _ = news_context_future.result()
        sym = _extract_ticker(task) or "MWG"
        started = time.time()
        try:
            content = _run_grok_news_cli(sym, progress, timeout=600)
            elapsed = time.time() - started
            progress(f"✅ GrokX News & Impact xong bằng Grok 9router API ({elapsed:.1f}s)")
            return {
                "agent": "grok",
                "name": MODEL3_NEWS.label,
                "action": "Grok 9router API news/direct-impact analyst | no_web_fallback",
                "content": content,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "elapsed": elapsed,
                "speaks_to": MODEL3_NEWS.speak_to,
                "framework": mode,
            }
        except Exception as exc:  # noqa: BLE001
            elapsed = time.time() - started
            progress(f"❌ GrokX News & Impact lỗi thật ({type(exc).__name__}); không dùng web fallback thay Grok.")
            return {
                "agent": "grok",
                "name": MODEL3_NEWS.label,
                "action": "GROK_NEWS_FAILED | no_web_fallback",
                "content": f"GROK_NEWS_FAILED: {type(exc).__name__}: {exc}. Không dùng nguồn thay thế để lấp phần tin; cần sửa Grok 9router API/search trước khi xuất bản tin tức.",
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "elapsed": elapsed,
                "speaks_to": MODEL3_NEWS.speak_to,
                "framework": mode,
            }

    # Grok/news is intentionally NOT in the blocking dependency path.
    # Hòa Đại ka requested: do not wait for Grok before investment scenarios.
    # Run it in the background as optional enrichment; TA/Fundamental unlock the rest.
    phase1_steps: list[AgentStep] = [
        MODEL3_ANALYSIS,
        MODEL3_FUNDAMENTAL,
    ]
    phase2_steps: list[AgentStep] = [
        MODEL3_SCENARIO,
        MODEL3_BULL_BEAR,
        MODEL3_RISK,
        MODEL3_FOLLOWUP_PLAN,
    ]
    # Only run the expensive tester when explicitly requested as a flag.
    # Vietnamese requests like "test thử cổ phiếu MWG" should test the report flow, not add a 9th AI branch.
    extra_steps: list[AgentStep] = []
    if _has_flag(task, "--test") or _has_flag(task, "/test"):
        extra_steps.append(MODEL3_TEST)
    if premium:
        extra_steps.append(CLAUDE_FINAL)

    def _run_step_group(steps: list[AgentStep], context: str, phase_label: str, offset: int, total: int) -> list[dict[str, Any]]:
        progress(f"🚦 {phase_label}: chạy song song {len(steps)} bot theo nhóm dependency đã sắp xếp.")
        futures: dict[Any, tuple[AgentStep, float]] = {}
        for pos, step_obj in enumerate(steps, 1):
            idx = offset + pos
            if step_obj.label == MODEL3_NEWS.label:
                fut = _EXECUTOR.submit(_run_news_branch)
            else:
                fut = _EXECUTOR.submit(_run_step, context, step_obj, [], progress, idx, total, mode)
            futures[fut] = (step_obj, time.time())
        group_posts: list[dict[str, Any]] = []
        for fut in concurrent.futures.as_completed(futures):
            step_obj, started = futures[fut]
            try:
                post = fut.result()
            except Exception as exc:  # noqa: BLE001
                post = _err(step_obj, exc, time.time() - started, mode)
                progress(f"❌ {step_obj.label} lỗi ({type(exc).__name__})")
            if post.get("name") == MODEL3_NEWS.label:
                post["content"] = _extract_marked_result(str(post.get("content", "")))
            group_posts.append(post)
        order = {step_obj.label: i for i, step_obj in enumerate(steps)}
        return sorted(group_posts, key=lambda p: order.get(p.get("name", ""), 99))

    total_steps = len(phase1_steps) + len(phase2_steps) + len(extra_steps) + 2  # + optional Grok + final summary
    posts: list[dict[str, Any]] = []

    progress("🛰️ GrokX News: chạy nền optional, không block kịch bản đầu tư.")
    news_future = _EXECUTOR.submit(_run_news_branch)

    phase1_posts = _run_step_group(phase1_steps, base_context, "Phase 1 nền — Technical / Fundamental (không chờ Grok)", 0, total_steps)
    for post in phase1_posts:
        _append(state, transcript, post)
        posts.append(post)

    phase1_context = base_context + "\n\nDỮ LIỆU NỀN ĐÃ CÓ CHO NHẬN ĐỊNH PHỤ THUỘC (KHÔNG CHỜ GROK):\n" + "\n\n".join(transcript[-8:])
    progress("🔗 Phase 2 dependency: Scenario/Bull-Bear/Risk/Follow-up chạy ngay sau TA/Fundamental; Grok nếu xong sẽ bổ sung sau.")
    phase2_posts = _run_step_group(phase2_steps + extra_steps, phase1_context, "Phase 2 kịch bản đầu tư — chạy song song, bỏ Grok khỏi critical path", len(phase1_steps), total_steps)
    for post in phase2_posts:
        _append(state, transcript, post)
        posts.append(post)

    # Non-blocking Grok enrichment: collect only if already done. Do not wait here.
    if news_future.done():
        try:
            news_post = news_future.result()
        except Exception as exc:  # noqa: BLE001
            news_post = _err(MODEL3_NEWS, exc, 0, mode)
        news_post["content"] = _extract_marked_result(str(news_post.get("content", "")))
        _append(state, transcript, news_post)
        posts.append(news_post)
        progress("✅ GrokX News đã xong kịp thời và được gắn vào báo cáo như enrichment.")
    else:
        progress("⏭️ GrokX News chưa xong; bỏ qua để không làm chậm báo cáo/kịch bản đầu tư.")
        news_future.cancel()
        skipped_news = {
            "agent": "grok",
            "name": MODEL3_NEWS.label,
            "action": "SKIPPED_NOT_BLOCKING | optional_enrichment_timeout",
            "content": "GrokX News chạy nền nhưng chưa xong tại thời điểm tổng hợp; báo cáo không chờ Grok theo cấu hình non-blocking.",
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "elapsed": 0,
            "speaks_to": MODEL3_NEWS.speak_to,
            "framework": mode,
        }
        _append(state, transcript, skipped_news)
        posts.append(skipped_news)

    progress("✅ Super_LH dependency graph: các phân tích chính đã xong; bắt đầu viết Executive Summary cuối cùng.")
    try:
        summary_context = base_context + "\n\nKẾT QUẢ PHÂN TÍCH CHÍNH ĐÃ HOÀN TẤT:\n" + "\n\n".join(transcript[-14:])
        summary_post = _run_step(summary_context, MODEL3_QUICK_SUMMARY, [], progress, total_steps, total_steps, mode)
    except Exception as exc:  # noqa: BLE001
        summary_post = _err(MODEL3_QUICK_SUMMARY, exc, 0, mode)
        progress(f"❌ {MODEL3_QUICK_SUMMARY.label} lỗi ({type(exc).__name__})")
    # Summary belongs at the top of the final report, but it must be generated last.
    state["feed"].insert(0, {"id": 1, **summary_post})
    for idx, item in enumerate(state["feed"], 1):
        item["id"] = idx
    transcript.insert(0, f"[{summary_post.get('agent')}] {summary_post.get('name')}:\n{summary_post.get('content', '')}")

    progress("✅ Model 3: xong phân tích chính và Executive Summary. Đang ghi DOCX theo template...")
    state = clean_vietnamese_object(state)
    docx_path = _write_docx(task, state)
    progress(f"✅ Model 3: đã ghi DOCX {docx_path}. Bot Telegram sẽ gửi file và xuất NotebookLM.")
    state["feed"].append({"id": len(state["feed"]) + 1, "agent": "system", "name": "Model 3 DOCX File", "action": "Đã lưu file DOCX", "content": f"Đã lưu file DOCX tại: {docx_path}", "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "elapsed": 0, "speaks_to": "NotebookLM/Người dùng", "framework": mode})
    return state


def run_hybrid_workflow(task: str, progress: ProgressFn) -> dict[str, Any]:
    if is_model3_task(task):
        return run_model3_workflow(task, progress)
    if is_model2_task(task):
        return run_debate_workflow(task, progress)
    return run_main_workflow(task, progress)

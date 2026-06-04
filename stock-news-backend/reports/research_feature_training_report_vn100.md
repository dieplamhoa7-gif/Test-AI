# Research Feature Training Report — VN100

Created: 2026-06-04T08:58:21.977024+00:00
Rows: 41,640
Rows with 20d label: 39,240

## Top feature observations vs futureReturn20d

- **sr_distSupportPct**: Spearman -0.2375; top20 avg -0.0193; bottom20 avg 0.0424; spread -0.0617; hit6 top/bottom 0.404 / 0.5018
- **sr_distResistancePct**: Spearman 0.2349; top20 avg 0.0675; bottom20 avg -0.0078; spread 0.0753; hit6 top/bottom 0.5556 / 0.3266
- **volatility_realizedVol20**: Spearman -0.101; top20 avg -0.0003; bottom20 avg 0.0222; spread -0.0224; hit6 top/bottom 0.4926 / 0.3543
- **volatility_atrPct**: Spearman -0.0998; top20 avg 0.0031; bottom20 avg 0.0225; spread -0.0193; hit6 top/bottom 0.5118 / 0.3369
- **trend_ret60**: Spearman -0.0677; top20 avg 0.019; bottom20 avg 0.0194; spread -0.0005; hit6 top/bottom 0.5436 / 0.4838
- **trend_ma50Slope20**: Spearman -0.0619; top20 avg 0.0117; bottom20 avg 0.0177; spread -0.0061; hit6 top/bottom 0.5249 / 0.4667
- **momentum_macdHistSlope3**: Spearman -0.0539; top20 avg 0.0052; bottom20 avg 0.0165; spread -0.0113; hit6 top/bottom 0.4393 / 0.4644
- **pattern_bullScore**: Spearman 0.0379; top20 avg 0.0151; bottom20 avg 0.0064; spread 0.0087; hit6 top/bottom 0.3886 / 0.4108
- **pattern_topPatternScore**: Spearman 0.0314; top20 avg 0.0151; bottom20 avg 0.0137; spread 0.0014; hit6 top/bottom 0.4329 / 0.4275
- **pattern_biasStrength**: Spearman 0.0281; top20 avg 0.0197; bottom20 avg 0.0146; spread 0.0051; hit6 top/bottom 0.4614 / 0.4313
- **trend_ret5**: Spearman -0.028; top20 avg 0.0139; bottom20 avg 0.0148; spread -0.0009; hit6 top/bottom 0.4783 / 0.4723
- **trend_ma20Slope20**: Spearman 0.0258; top20 avg 0.0191; bottom20 avg 0.0085; spread 0.0105; hit6 top/bottom 0.5344 / 0.4224

## Interpretation

- `sr_distSupportPct` âm khá rõ: càng xa hỗ trợ gần nhất thì future return 20d càng kém; nhóm gần hỗ trợ có avg return tốt hơn. Điều này ủng hộ hướng support-rebound/touch-zone nhưng cần kiểm OOS kỹ vì support hiện đang dùng snapshot pattern mới nhất, cần phiên bản rolling để production không leak.
- `sr_distResistancePct` dương khá rõ: còn nhiều room tới kháng cự thì future return tốt hơn; nếu sát kháng cự thì kém hơn. Đây là feature hợp lý cho risk/reward.
- Volatility (`atrPct`, `realizedVol20`) có tương quan âm nhẹ với future return trung bình, nhưng hit target 6% ở top vol lại cao hơn; nghĩa là vol cao có nhiều cơ hội chạy mạnh nhưng return trung bình/risk xấu hơn. Nên dùng vol cho sizing/risk, không đơn giản loại bỏ.
- Pattern score hiện có tín hiệu yếu hơn S/R distance. Pattern nên dùng như overlay/confluence, chưa nên làm tín hiệu chính nếu chưa có rolling backtest.

## High-correlation feature pairs

- trend_ret60 ↔ trend_ma50Slope20: 0.9333
- trend_priceVsMa20Pct ↔ momentum_rsi14: 0.9153
- trend_priceVsMa50Pct ↔ momentum_rsi14: 0.8986
- volatility_atrPct ↔ volatility_realizedVol20: 0.8779
- trend_ret20 ↔ momentum_rsi14: 0.846
- trend_ret20 ↔ trend_priceVsMa50Pct: 0.8244
- trend_ret20 ↔ trend_priceVsMa20Pct: 0.8171
- trend_ma20Slope20 ↔ trend_priceVsMa50Pct: 0.8123
- volatility_realizedVol20 ↔ volatility_bbWidth20: 0.7921
- trend_priceVsMa20Pct ↔ trend_priceVsMa50Pct: 0.7525
- trend_priceVsMa20Pct ↔ momentum_macdHist: 0.7508

## Regime summary

- symbolRegime=bearish: n=8090, avg20d=0.015, hit6=0.4031, avgDD=-0.0457
- symbolRegime=bullish: n=12930, avg20d=0.0119, hit6=0.4684, avgDD=-0.0636
- symbolRegime=sideway: n=18220, avg20d=0.0144, hit6=0.4093, avgDD=-0.0516
- volRegime=high: n=5591, avg20d=0.0012, hit6=0.5171, avgDD=-0.0792
- volRegime=low: n=4962, avg20d=0.0191, hit6=0.311, avgDD=-0.0318
- volRegime=normal: n=28687, avg20d=0.0152, hit6=0.4302, avgDD=-0.0534
- patternBias=bearish: n=7848, avg20d=0.0073, hit6=0.4332, avgDD=-0.0565
- patternBias=bullish: n=4578, avg20d=0.0349, hit6=0.4541, avgDD=-0.0477
- patternBias=neutral: n=26814, avg20d=0.0119, hit6=0.4213, avgDD=-0.0548

## Next steps

1. Fix potential leakage for S/R/pattern: build rolling pattern/SR features at each date, not latest snapshot only.
2. Backtest explicit strategies using these features: near-support + room-to-resistance + volatility filter.
3. Build feature correlation/PCA grouping to reduce duplicate indicators.
4. Add expected value metrics into strategy cache.
5. Only after OOS checks, consider simple ML probability model.
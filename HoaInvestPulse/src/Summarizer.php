<?php

declare(strict_types=1);

namespace HoaInvestPulse\Src;

class Summarizer
{
    private array $positiveKeywords = [
        'tăng', 'phục hồi', 'bứt phá', 'lạc quan', 'mở rộng', 'kỷ lục', 'tích cực'
    ];

    private array $negativeKeywords = [
        'giảm', 'lao dốc', 'rủi ro', 'khủng hoảng', 'áp lực', 'thua lỗ', 'suy yếu'
    ];

    public function summarizeCategory(array $items, string $label): array
    {
        if (empty($items)) {
            return [
                'headline' => "Chưa có dữ liệu mới cho {$label}.",
                'sentiment' => 'neutral',
                'key_points' => [],
            ];
        }

        $titles = array_map(fn($x) => mb_strtolower($x['title'] ?? '', 'UTF-8'), $items);
        $text = implode(' | ', $titles);

        $pos = $this->countKeywords($text, $this->positiveKeywords);
        $neg = $this->countKeywords($text, $this->negativeKeywords);

        $sentiment = 'neutral';
        if ($pos > $neg) {
            $sentiment = 'positive';
        } elseif ($neg > $pos) {
            $sentiment = 'negative';
        }

        $top = array_slice($items, 0, min(3, count($items)));
        $points = [];
        foreach ($top as $it) {
            $points[] = $it['title'];
        }

        return [
            'headline' => $this->buildHeadline($label, $sentiment, count($items)),
            'sentiment' => $sentiment,
            'key_points' => $points,
        ];
    }

    public function summarizeAll(array $allData): array
    {
        return [
            'stocks' => $this->summarizeCategory($allData['stocks'] ?? [], 'chứng khoán'),
            'economy' => $this->summarizeCategory($allData['economy'] ?? [], 'kinh tế'),
            'real_estate' => $this->summarizeCategory($allData['real_estate'] ?? [], 'BĐS'),
            'generated_at' => date(DATE_ATOM),
        ];
    }

    private function buildHeadline(string $label, string $sentiment, int $count): string
    {
        return match ($sentiment) {
            'positive' => "{$label}: xu hướng tích cực từ {$count} tin mới nhất.",
            'negative' => "{$label}: tâm lý thận trọng từ {$count} tin mới nhất.",
            default => "{$label}: diễn biến trung tính từ {$count} tin mới nhất.",
        };
    }

    private function countKeywords(string $text, array $keywords): int
    {
        $total = 0;
        foreach ($keywords as $kw) {
            $total += substr_count($text, mb_strtolower($kw, 'UTF-8'));
        }
        return $total;
    }
}

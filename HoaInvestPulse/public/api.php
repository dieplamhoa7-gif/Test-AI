<?php

declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');

require_once __DIR__ . '/../src/FeedService.php';
require_once __DIR__ . '/../src/Summarizer.php';

use HoaInvestPulse\Src\FeedService;
use HoaInvestPulse\Src\Summarizer;

$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 12;
$limit = max(5, min($limit, 30));

$cacheDir = __DIR__ . '/../storage/cache';

try {
    $feed = new FeedService($cacheDir);
    $sum = new Summarizer();

    $allNews = $feed->getAllNews($limit);
    $summaries = $sum->summarizeAll($allNews);

    echo json_encode([
        'ok' => true,
        'generated_at' => $summaries['generated_at'] ?? date(DATE_ATOM),
        'summaries' => [
            'stocks' => $summaries['stocks'] ?? [],
            'economy' => $summaries['economy'] ?? [],
            'real_estate' => $summaries['real_estate'] ?? [],
        ],
        'news' => $allNews,
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
} catch (Throwable $e) {
    http_response_code(500);
    echo json_encode([
        'ok' => false,
        'error' => 'Server error',
        'message' => $e->getMessage(),
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
}

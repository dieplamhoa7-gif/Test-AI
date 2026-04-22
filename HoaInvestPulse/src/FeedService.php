<?php

declare(strict_types=1);

namespace HoaInvestPulse\Src;

class FeedService
{
    private string $cacheDir;
    private int $cacheTtl = 300; // 5 phút

    private array $feeds = [
        'stocks' => [
            'https://cafef.vn/thi-truong-chung-khoan.rss',
            'https://vietstock.vn/rss/chung-khoan.rss',
        ],
        'economy' => [
            'https://vnexpress.net/rss/kinh-doanh.rss',
            'https://cafebiz.vn/vi-mo.rss',
        ],
        'real_estate' => [
            'https://vnexpress.net/rss/bat-dong-san.rss',
            'https://batdongsan.com.vn/feed',
        ],
    ];

    public function __construct(string $cacheDir)
    {
        $this->cacheDir = rtrim($cacheDir, DIRECTORY_SEPARATOR);
        if (!is_dir($this->cacheDir)) {
            mkdir($this->cacheDir, 0777, true);
        }
    }

    public function getCategoryNews(string $category, int $limit = 20): array
    {
        $category = strtolower($category);
        if (!isset($this->feeds[$category])) {
            return [];
        }

        $all = [];
        foreach ($this->feeds[$category] as $url) {
            $items = $this->fetchFeed($url);
            foreach ($items as $item) {
                $item['category'] = $category;
                $all[] = $item;
            }
        }

        usort($all, function ($a, $b) {
            return strtotime($b['published_at'] ?? '') <=> strtotime($a['published_at'] ?? '');
        });

        $unique = [];
        $seen = [];
        foreach ($all as $row) {
            $key = md5(($row['title'] ?? '') . '|' . ($row['link'] ?? ''));
            if (isset($seen[$key])) {
                continue;
            }
            $seen[$key] = true;
            $unique[] = $row;
            if (count($unique) >= $limit) {
                break;
            }
        }

        return $unique;
    }

    public function getAllNews(int $limitEach = 12): array
    {
        return [
            'stocks' => $this->getCategoryNews('stocks', $limitEach),
            'economy' => $this->getCategoryNews('economy', $limitEach),
            'real_estate' => $this->getCategoryNews('real_estate', $limitEach),
        ];
    }

    private function fetchFeed(string $url): array
    {
        $xmlString = $this->getCachedOrFetch($url);
        if (!$xmlString) {
            return [];
        }

        libxml_use_internal_errors(true);
        $xml = simplexml_load_string($xmlString, 'SimpleXMLElement', LIBXML_NOCDATA);
        if (!$xml) {
            return [];
        }

        $items = [];

        if (isset($xml->channel->item)) {
            foreach ($xml->channel->item as $item) {
                $items[] = $this->normalizeItem($item, parse_url($url, PHP_URL_HOST) ?: 'unknown');
            }
        } elseif (isset($xml->entry)) {
            foreach ($xml->entry as $entry) {
                $items[] = $this->normalizeAtomEntry($entry, parse_url($url, PHP_URL_HOST) ?: 'unknown');
            }
        }

        return array_values(array_filter($items));
    }

    private function normalizeItem(\SimpleXMLElement $item, string $source): ?array
    {
        $title = trim((string)($item->title ?? ''));
        $link = trim((string)($item->link ?? ''));
        $desc = trim(strip_tags((string)($item->description ?? '')));
        $pubDate = trim((string)($item->pubDate ?? ''));

        if ($title === '' || $link === '') {
            return null;
        }

        return [
            'title' => $title,
            'link' => $link,
            'description' => $desc,
            'published_at' => $this->toIsoTime($pubDate),
            'source' => $source,
        ];
    }

    private function normalizeAtomEntry(\SimpleXMLElement $entry, string $source): ?array
    {
        $title = trim((string)($entry->title ?? ''));
        $link = '';

        if (isset($entry->link)) {
            foreach ($entry->link as $ln) {
                $attrs = $ln->attributes();
                if (isset($attrs['href'])) {
                    $link = (string)$attrs['href'];
                    break;
                }
            }
        }

        $summary = trim(strip_tags((string)($entry->summary ?? $entry->content ?? '')));
        $published = trim((string)($entry->published ?? $entry->updated ?? ''));

        if ($title === '' || $link === '') {
            return null;
        }

        return [
            'title' => $title,
            'link' => $link,
            'description' => $summary,
            'published_at' => $this->toIsoTime($published),
            'source' => $source,
        ];
    }

    private function toIsoTime(string $time): string
    {
        $ts = strtotime($time);
        if ($ts === false) {
            return date(DATE_ATOM);
        }
        return date(DATE_ATOM, $ts);
    }

    private function getCachedOrFetch(string $url): ?string
    {
        $cacheFile = $this->cacheDir . DIRECTORY_SEPARATOR . md5($url) . '.xml';

        if (is_file($cacheFile) && (time() - filemtime($cacheFile) < $this->cacheTtl)) {
            $cached = file_get_contents($cacheFile);
            if ($cached !== false) {
                return $cached;
            }
        }

        $context = stream_context_create([
            'http' => [
                'method' => 'GET',
                'timeout' => 8,
                'header' => "User-Agent: HoaInvestPulseBot/1.0\r\nAccept: application/rss+xml, application/xml, text/xml, */*\r\n",
            ],
            'ssl' => [
                'verify_peer' => true,
                'verify_peer_name' => true,
            ],
        ]);

        $content = @file_get_contents($url, false, $context);
        if ($content === false || trim($content) === '') {
            if (is_file($cacheFile)) {
                $stale = file_get_contents($cacheFile);
                return $stale !== false ? $stale : null;
            }
            return null;
        }

        file_put_contents($cacheFile, $content);
        return $content;
    }
}

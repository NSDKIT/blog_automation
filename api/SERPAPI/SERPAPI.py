import requests
import json

# リクエストパターンのリスト
request_patterns = [
    {
        "url": "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
        "payload": [{
            "keyword": "weather forecast",
            "location_code": 2392,
            "language_code": "ja",
            "device": "desktop",
            "os": "windows",
            "depth": 100
        }]
    },
    {
        "url": "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
        "payload": [{
            "keyword": "weather forecast",
            "location_code": 2392,
            "language_code": "ja",
            "device": "desktop",
            "os": "macos",
            "depth": 100
        }]
    },
    {
        "url": "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
        "payload": [{
            "keyword": "weather forecast",
            "location_code": 2392,
            "language_code": "ja",
            "device": "mobile",
            "os": "android",
            "depth": 100
        }]
    },
    {
        "url": "https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
        "payload": [{
            "keyword": "weather forecast",
            "location_code": 2392,
            "language_code": "ja",
            "device": "mobile",
            "os": "ios",
            "depth": 100
        }]
    },
    {
        "url": "https://api.dataforseo.com/v3/serp/bing/organic/live/advanced",
        "payload": [{
            "keyword": "weather forecast",
            "location_code": 2392,
            "language_code": "ja",
            "device": "desktop",
            "os": "windows",
            "depth": 100
        }]
    },
    {
        "url": "https://api.dataforseo.com/v3/serp/bing/organic/live/advanced",
        "payload": [{
            "keyword": "weather forecast",
            "location_code": 2392,
            "language_code": "ja",
            "device": "desktop",
            "os": "macos",
            "depth": 100
        }]
    },
    {
        "url": "https://api.dataforseo.com/v3/serp/bing/organic/live/advanced",
        "payload": [{
            "keyword": "weather forecast",
            "location_code": 2392,
            "language_code": "ja",
            "device": "mobile",
            "os": "android",
            "depth": 100
        }]
    },
    {
        "url": "https://api.dataforseo.com/v3/serp/bing/organic/live/advanced",
        "payload": [{
            "keyword": "weather forecast",
            "location_code": 2392,
            "language_code": "ja",
            "device": "mobile",
            "os": "ios",
            "depth": 100
        }]
    },
]

headers = {
    'Authorization': 'Basic bnNka2l0MDIyNEBnbWFpbC5jb206M2EyOGE3ODIxMTEyOWEwZQ==',
    'Content-Type': 'application/json'
}

# レスポンスデータリスト
results = []

for pattern in request_patterns:
    url = pattern["url"]
    payload = json.dumps(pattern["payload"], ensure_ascii=False)
    response = requests.post(url, headers=headers, data=payload)
    result = {
        "url": url,
        "payload": payload,
        "headers": headers,
        "response_text": response.text
    }
    results.append(result)

# 結果を表示・保存
# 例：各リクエストのurl, payload, headers, responseをJSON形式でファイルに保存
with open("serpapi_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# 必要であればprintで確認
for res in results:
    print("="*40)
    print(f"url: {res['url']}")
    print(f"payload: {res['payload']}")
    print(f"headers: {res['headers']}")
    print(f"response_text: {res['response_text'][:300]} ...")  # 長い場合は先頭だけ
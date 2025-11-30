import requests
import json

# リクエストパターンのリスト
request_patterns = [
    {
        "endpoint": "https://api.dataforseo.com/v3/dataforseo_labs/google/related_keywords/live",
        "payload": [{
            "keyword": "seo",
            "location_code": 2392,
            "language_code": "ja",
            "depth": 3,
            "include_seed_keyword": False,
            "include_serp_info": False,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "replace_with_core_keyword": False,
            "limit": 100,
        }],
    },
    {
        "endpoint": "https://api.dataforseo.com/v3/dataforseo_labs/google/keywords_for_site/live",
        "payload": [{
            "target": "dataforseo.com",
            "location_code": 2392,
            "language_code": "ja",
            "include_serp_info": False,
            "include_subdomains": True,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "limit": 100,
        }],
    },
    {
        "endpoint": "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_suggestions/live",
        "payload": [{
            "keyword": "seo",
            "location_code": 2392,
            "language_code": "ja",
            "include_seed_keyword": False,
            "include_serp_info": False,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "exact_match": False,
            "limit": 100,
        }],
    },
    {
        "endpoint": "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live",
        "payload": [{
            "keywords": ["seo"],
            "location_code": 2392,
            "language_code": "ja",
            "include_serp_info": False,
            "closely_variants": False,
            "ignore_synonyms": False,
            "include_clickstream_data": False,
            "limit": 100,
        }],
    }
]

headers = {
    'Authorization': 'Basic bnNka2l0MDIyNEBnbWFpbC5jb206M2EyOGE3ODIxMTEyOWEwZQ==',
    'Content-Type': 'application/json'
}

results = []

for pattern in request_patterns:
    url = pattern["endpoint"]
    payload = json.dumps(pattern["payload"], ensure_ascii=False)
    response = requests.post(url, headers=headers, data=payload)
    result = {
        "url": url,
        "payload": payload,
        "headers": headers,
        "response_text": response.text
    }
    results.append(result)

# レスポンスをファイルに保存（任意）
with open("domainanalyticsapi_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# 必要であればprintで確認
for res in results:
    print("="*40)
    print(f"url: {res['url']}")
    print(f"payload: {res['payload']}")
    print(f"headers: {res['headers']}")
    print(f"response_text: {res['response_text'][:300]} ...")  # 長い場合は先頭だけ

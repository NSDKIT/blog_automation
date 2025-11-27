import requests

results = {}

requests_data = [
    {
        "name": "response1",
        "url": "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live",
        "payload": '[{"keywords":["weather forecast"], "sort_by":"relevance"}]',
    },
    {
        "name": "response2",
        "url": "https://api.dataforseo.com/v3/keywords_data/google_ads/keywords_for_site/live",
        "payload": '[{"target":"dataforseo.com", "location_code":2392, "language_code":"ja", "sort_by":"relevance"}]',
    },
    {
        "name": "response3",
        "url": "https://api.dataforseo.com/v3/keywords_data/google_ads/keywords_for_keywords/live",
        "payload": '[{"keywords":["weather forecast"], "sort_by":"relevance"}]',
    },
    {
        "name": "response4",
        "url": "https://api.dataforseo.com/v3/keywords_data/google_trends/explore/live",
        "payload": '[{"keywords":["weather forecast"]}]',
    },
    {
        "name": "response5",
        "url": "https://api.dataforseo.com/v3/keywords_data/dataforseo_trends/explore/live",
        "payload": '[{"keywords":["weather forecast"], "location_code":2392}]',
    },
]

headers = {
    'Authorization': 'Basic bnNka2l0MDIyNEBnbWFpbC5jb206M2EyOGE3ODIxMTEyOWEwZQ==',
    'Content-Type': 'application/json'
}

for req in requests_data:
    response = requests.post(req["url"], headers=headers, data=req["payload"])
    results[req["name"]] = {
        "url": req["url"],
        "payload": req["payload"],
        "headers": dict(headers),  # to ensure plain dict (not share reference)
        "response_text": response.text,
    }

# 例: 出力や保存用
import json
with open("keyworddataapi_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
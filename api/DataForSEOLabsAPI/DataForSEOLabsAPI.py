import requests
import json

class DataForSEOLabsAPI:
    BASE_URL = "https://api.dataforseo.com/v3/dataforseo_labs/google"
    AUTH_HEADER = {
        'Authorization': 'Basic bnNka2l0MDIyNEBnbWFpbC5jb206M2EyOGE3ODIxMTEyOWEwZQ==',
        'Content-Type': 'application/json'
    }

    @staticmethod
    def _post(endpoint, payload):
        url = f"{DataForSEOLabsAPI.BASE_URL}{endpoint}"
        response = requests.post(url, headers=DataForSEOLabsAPI.AUTH_HEADER, data=payload)
        return {
            "url": url,
            "payload": payload,
            "headers": DataForSEOLabsAPI.AUTH_HEADER,
            "response_text": response.text
        }

    def related_keywords(self, keyword="seo", location_code=2392, language_code="ja"):
        payload = f"""[{{"keyword":"{keyword}", "location_code":{location_code}, "language_code":"{language_code}", "depth":3, "include_seed_keyword":false, "include_serp_info":false, "ignore_synonyms":false, "include_clickstream_data":false, "replace_with_core_keyword":false, "limit":100}}]"""
        return self._post("/related_keywords/live", payload)

    def keywords_for_site(self, target="dataforseo.com", location_code=2392, language_code="ja"):
        payload = f"""[{{"target":"{target}", "location_code":{location_code}, "language_code":"{language_code}", "include_serp_info":false, "include_subdomains":true, "ignore_synonyms":false, "include_clickstream_data":false, "limit":100}}]"""
        return self._post("/keywords_for_site/live", payload)

    def keyword_suggestions(self, keyword="seo", location_code=2392, language_code="ja"):
        payload = f"""[{{"keyword":"{keyword}", "location_code":{location_code}, "language_code":"{language_code}", "include_seed_keyword":false, "include_serp_info":false, "ignore_synonyms":false, "include_clickstream_data":false, "exact_match":false, "limit":100}}]"""
        return self._post("/keyword_suggestions/live", payload)

    def keyword_ideas(self, keywords=["seo"], location_code=2392, language_code="ja"):
        kws = ",".join([f'"{kw}"' for kw in keywords])
        payload = f"""[{{"keywords":[{kws}], "location_code":{location_code}, "language_code":"{language_code}", "include_serp_info":false, "closely_variants":false, "ignore_synonyms":false, "include_clickstream_data":false, "limit":100}}]"""
        return self._post("/keyword_ideas/live", payload)

    def historical_keyword_data(self, keywords=["seo"], location_code=2392, language_code="ja"):
        kws = ",".join([f'"{kw}"' for kw in keywords])
        payload = f"""[{{"keywords":[{kws}], "location_code":{location_code}, "language_code":"{language_code}"}}]"""
        return self._post("/historical_keyword_data/live", payload)

    def keyword_overview(self, keywords=["seo"], location_code=2392, language_code="ja"):
        kws = ",".join([f'"{kw}"' for kw in keywords])
        payload = f"""[{{"keywords":[{kws}], "location_code":{location_code}, "language_code":"{language_code}", "include_serp_info":false, "include_clickstream_data":false}}]"""
        return self._post("/keyword_overview/live", payload)

    def bulk_keyword_difficulty(self, keywords=["seo"], location_code=2392, language_code="ja"):
        kws = ",".join([f'"{kw}"' for kw in keywords])
        payload = f"""[{{"keywords":[{kws}], "location_code":{location_code}, "language_code":"{language_code}"}}]"""
        return self._post("/bulk_keyword_difficulty/live", payload)

    def categories_for_domain(self, target="dataforseo.com", location_code=2392, language_code="ja"):
        payload = f"""[{{"target":"{target}", "location_code":{location_code}, "language_code":"{language_code}", "include_clickstream_data":false, "include_subcategories":false, "limit":100}}]"""
        return self._post("/categories_for_domain/live", payload)

    def keywords_for_categories(self, category_codes=[10013], location_code=2392, language_code="ja"):
        cats = ",".join(map(str, category_codes))
        payload = f"""[{{"category_codes":[{cats}], "location_code":{location_code}, "language_code":"{language_code}", "include_serp_info":false, "ignore_synonyms":false, "include_clickstream_data":false, "category_intersection":true, "limit":100}}]"""
        return self._post("/keywords_for_categories/live", payload)

    def domain_metrics_by_categories(self, category_codes=[10013], location_code=2392, language_code="ja"):
        cats = ",".join(map(str, category_codes))
        payload = f"""[{{"category_codes":[{cats}], "location_code":{location_code}, "language_code":"{language_code}", "include_subdomains":true, "limit":100, "first_date":"2021-06-01", "second_date":"2021-10-01", "etv_min":10000, "etv_max":100000, "top_categories_count":1, "correlate":true}}]"""
        return self._post("/domain_metrics_by_categories/live", payload)

    def top_searches(self, location_code=2392, language_code="ja"):
        payload = f"""[{{"location_code":{location_code}, "language_code":"{language_code}", "include_serp_info":false, "ignore_synonyms":false, "include_clickstream_data":false, "limit":100}}]"""
        return self._post("/top_searches/live", payload)

    def ranked_keywords(self, target="dataforseo.com", location_code=2392, language_code="ja"):
        payload = f"""[{{"target":"{target}", "location_code":{location_code}, "language_code":"{language_code}", "historical_serp_mode":"live", "ignore_synonyms":false, "include_clickstream_data":false, "load_rank_absolute":false, "limit":100}}]"""
        return self._post("/ranked_keywords/live", payload)

    def serp_competitors(self, keywords=["seo"], location_code=2392, language_code="ja"):
        kws = ",".join([f'"{kw}"' for kw in keywords])
        payload = f"""[{{"keywords":[{kws}], "location_code":{location_code}, "language_code":"{language_code}", "include_subdomains":true, "limit":100}}]"""
        return self._post("/serp_competitors/live", payload)

    def competitors_domain(self, target="dataforseo.com", location_code=2392, language_code="ja"):
        payload = f"""[{{"target":"{target}", "location_code":{location_code}, "language_code":"{language_code}", "exclude_top_domains":false, "ignore_synonyms":false, "include_clickstream_data":false, "limit":100}}]"""
        return self._post("/competitors_domain/live", payload)

    def domain_intersection(self, target1="dataforseo.com", target2="seopanel.org", location_code=2392, language_code="ja"):
        payload = f"""[{{"target1":"{target1}", "target2":"{target2}", "location_code":{location_code}, "language_code":"{language_code}", "include_serp_info":false, "include_clickstream_data":false, "intersections":true, "limit":100}}]"""
        return self._post("/domain_intersection/live", payload)

    def subdomains(self, target="dataforseo.com", location_code=2392, language_code="ja"):
        payload = f"""[{{"target":"{target}", "location_code":{location_code}, "language_code":"{language_code}", "historical_serp_mode":"live", "ignore_synonyms":false, "include_clickstream_data":false, "limit":100}}]"""
        return self._post("/subdomains/live", payload)

    def relevant_pages(self, target="dataforseo.com", location_code=2392, language_code="ja"):
        payload = f"""[{{"target":"{target}", "location_code":{location_code}, "language_code":"{language_code}", "historical_serp_mode":"live", "ignore_synonyms":false, "include_clickstream_data":false, "limit":100}}]"""
        return self._post("/relevant_pages/live", payload)

    def domain_rank_overview(self, target="dataforseo.com", location_code=2392, language_code="ja"):
        payload = f"""[{{"target":"{target}", "location_code":{location_code}, "language_code":"{language_code}", "ignore_synonyms":false, "limit":100}}]"""
        return self._post("/domain_rank_overview/live", payload)

    def historical_rank_overview(self, target="dataforseo.com", location_code=2392, language_code="ja"):
        payload = f"""[{{"target":"{target}", "location_code":{location_code}, "language_code":"{language_code}", "ignore_synonyms":false, "include_clickstream_data":false, "correlate":true}}]"""
        return self._post("/historical_rank_overview/live", payload)

    def page_intersection(self, pages=None, location_code=2392, language_code="ja"):
        if pages is None:
            pages = {"1": "https://dataforseo.com", "2": "https://seopanel.org/*"}
        pages_obj = ", ".join([f'"{k}":"{v}"' for k, v in pages.items()])
        payload = f"""[{{"pages":{{{pages_obj}}}, "location_code":{location_code}, "language_code":"{language_code}", "include_serp_info":false, "include_subdomains":true, "intersection_mode":"intersect", "ignore_synonyms":false, "include_clickstream_data":false, "limit":100}}]"""
        return self._post("/page_intersection/live", payload)

    def bulk_traffic_estimation(self, targets=["dataforseo.com"], location_code=2392, language_code="ja"):
        tgts = ",".join([f'"{t}"' for t in targets])
        payload = f"""[{{"targets":[{tgts}], "location_code":{location_code}, "language_code":"{language_code}", "ignore_synonyms":false}}]"""
        return self._post("/bulk_traffic_estimation/live", payload)

    def historical_bulk_traffic_estimation(self, targets=["dataforseo.com"], location_code=2392, language_code="ja"):
        tgts = ",".join([f'"{t}"' for t in targets])
        payload = f"""[{{"targets":[{tgts}], "location_code":{location_code}, "language_code":"{language_code}", "ignore_synonyms":false}}]"""
        return self._post("/historical_bulk_traffic_estimation/live", payload)

    def historical_serps(self, keyword="seo", location_code=2392, language_code="ja"):
        payload = f"""[{{"keyword":"{keyword}", "location_code":{location_code}, "language_code":"{language_code}"}}]"""
        return self._post("/historical_serps/live", payload)

    def search_intent(self, keywords=["seo"], language_code="ar"):
        kws = ",".join([f'"{kw}"' for kw in keywords])
        payload = f"""[{{"keywords":[{kws}], "language_code":"{language_code}"}}]"""
        return self._post("/search_intent/live", payload)

    def categories_for_keywords(self, keywords=["seo"], language_code="ar"):
        kws = ",".join([f'"{kw}"' for kw in keywords])
        payload = f"""[{{"keywords":[{kws}], "language_code":"{language_code}"}}]"""
        return self._post("/categories_for_keywords/live", payload)

# For test/demo:
if __name__ == "__main__":
    api = DataForSEOLabsAPI()
    request_patterns = [
        {"func": api.related_keywords, "args": (), "kwargs": {}},
        {"func": api.keywords_for_site, "args": (), "kwargs": {}},
        {"func": api.keyword_suggestions, "args": (), "kwargs": {}},
        {"func": api.keyword_ideas, "args": (), "kwargs": {}},
        {"func": api.historical_keyword_data, "args": (), "kwargs": {}},
        {"func": api.keyword_overview, "args": (), "kwargs": {}},
        {"func": api.bulk_keyword_difficulty, "args": (), "kwargs": {}},
        {"func": api.categories_for_domain, "args": (), "kwargs": {}},
        {"func": api.keywords_for_categories, "args": (), "kwargs": {}},
        {"func": api.domain_metrics_by_categories, "args": (), "kwargs": {}},
        {"func": api.top_searches, "args": (), "kwargs": {}},
        {"func": api.ranked_keywords, "args": (), "kwargs": {}},
        {"func": api.serp_competitors, "args": (), "kwargs": {}},
        {"func": api.competitors_domain, "args": (), "kwargs": {}},
        {"func": api.domain_intersection, "args": (), "kwargs": {}},
        {"func": api.subdomains, "args": (), "kwargs": {}},
        {"func": api.relevant_pages, "args": (), "kwargs": {}},
        {"func": api.domain_rank_overview, "args": (), "kwargs": {}},
        {"func": api.historical_rank_overview, "args": (), "kwargs": {}},
        {"func": api.page_intersection, "args": (), "kwargs": {}},
        {"func": api.bulk_traffic_estimation, "args": (), "kwargs": {}},
        {"func": api.historical_bulk_traffic_estimation, "args": (), "kwargs": {}},
        {"func": api.historical_serps, "args": (), "kwargs": {}},
        {"func": api.search_intent, "args": (), "kwargs": {}},
        {"func": api.categories_for_keywords, "args": (), "kwargs": {}}
    ]

    results = []

    for pattern in request_patterns:
        res = pattern["func"](*pattern["args"], **pattern["kwargs"])
        results.append(res)

    # 全てのレスポンスを一つのファイルに保存する
    with open("dataforseolabsapi_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 必要であればprintで確認
    for res in results:
        print("="*40)
        print(f"url: {res['url']}")
        print(f"payload: {res['payload']}")
        print(f"headers: {res['headers']}")
        print(f"response_text: {res['response_text'][:300]} ...")  # 長い場合は先頭だけ

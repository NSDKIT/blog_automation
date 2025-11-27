import requests

url = "https://api.dataforseo.com/v3/dataforseo_labs/google/related_keywords/live"

payload="[{\"keyword\":\"seo\", \"location_code\":2392, \"language_code\":\"ja\", \"depth\":3, \"include_seed_keyword\":false, \"include_serp_info\":false, \"ignore_synonyms\":false, \"include_clickstream_data\":false, \"replace_with_core_keyword\":false, \"limit\":100}]"
headers = {
	'Authorization': 'Basic bnNka2l0MDIyNEBnbWFpbC5jb206M2EyOGE3ODIxMTEyOWEwZQ==',
	'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

import requests

url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keywords_for_site/live"

payload="[{\"target\":\"dataforseo.com\", \"location_code\":2392, \"language_code\":\"ja\", \"include_serp_info\":false, \"include_subdomains\":true, \"ignore_synonyms\":false, \"include_clickstream_data\":false, \"limit\":100}]"
headers = {
	'Authorization': 'Basic bnNka2l0MDIyNEBnbWFpbC5jb206M2EyOGE3ODIxMTEyOWEwZQ==',
	'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

import requests

url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_suggestions/live"

payload="[{\"keyword\":\"seo\", \"location_code\":2392, \"language_code\":\"ja\", \"include_seed_keyword\":false, \"include_serp_info\":false, \"ignore_synonyms\":false, \"include_clickstream_data\":false, \"exact_match\":false, \"limit\":100}]"
headers = {
	'Authorization': 'Basic bnNka2l0MDIyNEBnbWFpbC5jb206M2EyOGE3ODIxMTEyOWEwZQ==',
	'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

import requests

url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live"

payload="[{\"keywords\":[\"seo\"], \"location_code\":2392, \"language_code\":\"ja\", \"include_serp_info\":false, \"closely_variants\":false, \"ignore_synonyms\":false, \"include_clickstream_data\":false, \"limit\":100}]"
headers = {
	'Authorization': 'Basic bnNka2l0MDIyNEBnbWFpbC5jb206M2EyOGE3ODIxMTEyOWEwZQ==',
	'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)


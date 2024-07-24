import requests, os

headers = {
    'Authorization': os.getenv("SPIDER_API_KEY"),
    'Content-Type': 'application/json'
}

json_data = {"url":"https://news.ycombinator.com"}

response = requests.post('https://api.spider.cloud/data/query', 
  headers=headers, 
  json=json_data)

print(response.json())
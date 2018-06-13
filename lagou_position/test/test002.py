import requests

headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"}
url = 'http://m.lagou.com/jobs/4571688.html'
# proxy = requests.get('http://127.0.0.1:5555/random').text
proxy = '183.149.71.32:40940'
proxies = {'http':'http://{}'.format(proxy),'https':'https://{}'.format(proxy)}

html = requests.get(url = 'http://m.lagou.com/jobs/4571688.html',headers=headers)
print(html.text)
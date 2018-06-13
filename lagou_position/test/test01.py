import json
import requests
from requests.exceptions import RequestException
import re
import time

def crawl_xdaili1():
    url = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=f6031410e7614e6cbeb026b25b72ab13&orderno=YZ201861353930WtPtt&returnType=2&count=1'
    html = requests.get(url).text
    if html:
        result = json.loads(html)
        proxies = result.get('RESULT')
        for proxy in proxies:
            return proxy.get('ip') + ':' + proxy.get('port')


if __name__ == '__main__':
    proxy = crawl_xdaili1()
    proxies = {'http':'http://{}'.format(proxy),'https':'https://{}'.format(proxy)}
    print(proxies)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"}
    url = 'http://m.lagou.com/jobs/4571688.html'
    html = requests.get(url='http://m.lagou.com/jobs/4571688.html', proxies=proxies,headers=headers)
    print(html.text)



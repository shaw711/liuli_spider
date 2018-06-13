import requests

# 要访问的目标页面
targetUrl = "http://test.abuyun.com"

# 代理服务器
proxyHost = "http-dyn.abuyun.com"
proxyPort = "9010"

# 代理隧道验证信息
proxyUser = "HN6IW6M45415S09P"
proxyPass = "DB632F2EA608572C"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}

proxies = {
    "http": proxyMeta,
    "https": proxyMeta,
}

resp = requests.get(targetUrl, proxies=proxies)

print (resp.status_code)
print (resp.text)

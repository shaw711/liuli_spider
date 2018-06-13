# -*- coding:utf-8 -*-
__author__ = 'mangu'

import hashlib
import re
import sqlite3
import requests
import json

def get_md5(url):
    #python3 中 str就是unicode了
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    #从字符串中提取出数字
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums




# conn = sqlite3.connect('D:/tools/2018.2/IPProxyPool-master/data/proxy.db')
# cur = conn.cursor()
#
# class GetIP(object):
#     def get_ip(self):
#         random_sql = """
#         SELECT ip,port FROM proxys
#         ORDER BY RANDOM()
#         LIMIT 1
#         """
#         result = cur.execute(random_sql)
#         for ip_info in cur.fetchall():
#             ip = ip_info[0]
#             port = ip_info[1]
#             return "http://{0}:{1}".format(ip, port)

if __name__ == "__main__":
    print(get_md5("http://jobbole.com".encode("utf-8")))
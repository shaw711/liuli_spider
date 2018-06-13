# -*- coding: utf-8 -*-
from scrapy import Request,Spider
import json
from lagou_position.items import LagouPositionItem,LagouLoader
from lagou_position.utils.common import get_md5
import datetime
import requests

class LagouSpider(Spider):
    name = 'lagou'
    allowed_domains = ['m.lagou.com']
    start_urls = ['http://m.lagou.com/jobs/4704505.html']

    custom_settings = {
        # "REDIRECT_ENABLED" : False,
        "HTTPERROR_ALLOWED_CODES" : '302',
        "COOKIES_ENABLED": False,
    }

    def start_requests(self):
        for page in range(1,62):
            '''第1页到第61页有数据'''
            url = 'http://m.lagou.com/search.json?city=%E5%8C%97%E4%BA%AC&positionName=python%E7%88%AC%E8%99%AB&pageNo={page}&pageSize=15'.format(page=page)
            yield Request(url=url,callback=self.parse)

    def parse(self, response):
        try:
            headers = {
                # "Cookie": "JSESSIONID=ABAAABAAAFDABFG470F4B4E7E7603362F9AB0881E8A1021; user_trace_token=20180613144300-a2b69755-f781-4e30-b615-15f318ccffb5; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1528872181; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1528872181; _ga=GA1.3.1938898543.1528872181; _gat=1; LGSID=20180613144300-04086368-6ed5-11e8-9d3b-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=http%3A%2F%2Fm.lagou.com%2Fjobs%2F4714553.html; LGRID=20180613144300-0408669d-6ed5-11e8-9d3b-525400f775ce; LGUID=20180613144300-0408670a-6ed5-11e8-9d3b-525400f775ce; _ga=GA1.2.1938898543.1528872181; _gid=GA1.2.989832180.1528872181",
                # "Host": "m.lagou.com",
                # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36",
                "Referer": "http://m.lagou.com/search.html"
            }
            result = json.loads(response.body_as_unicode())["content"]["data"]["page"]["result"]
            for i in result:
                positionId = i["positionId"]
                positionName = i["positionName"]
                companyName = i["companyName"]
                companyFullName = i["companyFullName"]
                createTime = i["createTime"]
                url = 'http://m.lagou.com/jobs/{positionId}.html'.format(positionId=positionId)

                '''meta可以传递很多数据'''
                yield Request(url=url, callback=self.parse_detail,headers=headers,
                              meta={"positionName": positionName, "companyName": companyName,
                                    "companyFullName": companyFullName, "createTime": createTime})
        except:
            pass


    def parse_detail(self,response):

        positionName = response.request.meta.get('positionName','母鸡')
        companyName = response.request.meta.get('companyName','母鸡')
        companyFullName = response.request.meta.get('companyFullName','母鸡')
        createTime = response.request.meta.get('createTime',datetime.date(2020, 6, 11))

        item_loader = LagouLoader(item=LagouPositionItem(),response=response)
        item_loader.add_value('positionName',positionName)
        item_loader.add_value('companyName',companyName)
        item_loader.add_value('companyFullName',companyFullName)
        item_loader.add_value('createTime',createTime)
        item_loader.add_css('salary','.detail .items > span.item.salary > span::text')
        item_loader.add_css('work_time','.detail  .items > span.item.salary > span::text')
        item_loader.add_css('education','.detail .items > span.item.education > span::text')
        item_loader.add_css('locals','.detail .items > span.item.workaddress > span::text')
        item_loader.add_xpath('work_description','//*[@id="content"]/div[4]/div/p//text()')
        item_loader.add_xpath('company_description','//*[@id="content"]/div[3]/div/div/p/text()')
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        article_item = item_loader.load_item()
        yield article_item









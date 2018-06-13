# -*- coding: utf-8 -*-
import scrapy
from tutorial.items import ChengdeItem,ChengdeItemLoader
from tutorial.utils.common import get_md5

from pyquery import PyQuery as pq

'''58爬虫，承德地区租房信息'''
class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['chengde.58.com','jxjump.58.com','short.58.com']
    start_urls = ['http://chengde.58.com/chuzu/']

    def start_requests(self):
        base_url = ['http://chengde.58.com/chengdeshi/chuzu/','http://chengde.58.com/cdshuangqiao/chuzu/','http://chengde.58.com/chengdexian/chuzu/','http://chengde.58.com/luanpingxian/chuzu/',
                    'http://chengde.58.com/weichangxian/chuzu/','http://chengde.58.com/xinglongxian/chuzu/','http://chengde.58.com/fengningxian/chuzu/','http://chengde.58.com/pingquanxian/chuzu/',
                    'http://chengde.58.com/longhuaxian/chuzu/','http://chengde.58.com/kuanchengxian/chuzu/','http://chengde.58.com/shuangluan/chuzu/','http://chengde.58.com/yingzi/chuzu/',
                    'http://chengde.58.com/cdkaifaqu/chuzu/','http://chengde.58.com/chengdezb/chuzu/']
        # '''http://chengde.58.com/chengdeshi/chuzu/','http://chengde.58.com/cdshuangqiao/chuzu/','http://chengde.58.com/chengdexian/chuzu/','http://chengde.58.com/luanpingxian/chuzu/',
        #             'http://chengde.58.com/weichangxian/chuzu/','http://chengde.58.com/xinglongxian/chuzu/','http://chengde.58.com/fengningxian/chuzu/','http://chengde.58.com/pingquanxian/chuzu/',
        #             'http://chengde.58.com/longhuaxian/chuzu/','http://chengde.58.com/kuanchengxian/chuzu/','http://chengde.58.com/shuangluan/chuzu/','http://chengde.58.com/yingzi/chuzu/',
        #             'http://chengde.58.com/cdkaifaqu/chuzu/','http://chengde.58.com/chengdezb/chuzu/'''
        for url in base_url:
            yield scrapy.Request(url, self.parse)


    def parse(self, response):
        html = pq(response.text)
        for each in html('body > div.mainbox > div.main > div.content > div.listBox > ul > li > div.des > h2 > a:first-child').items():
            if each:
                '''不在此域名之下，不过滤 ,dont_filter=True'''
                yield scrapy.Request(url=each.attr.href,callback=self.parse_detail,dont_filter=True)
        next = html('.next').attr.href
        if next:
            yield scrapy.Request(url=next, callback=self.parse)

    def parse_detail(self,response):
        html = pq(response.text)
        detail = html(".house-detail-desc  .main-detail-info.fl .house-word-introduce.f16.c_555 > ul").text()
        telephone = response.css(".house-basic-info .house-fraud-tip > div.house-chat-phone > span::text").extract_first("扫描查看")

        chengde_loader = ChengdeItemLoader(item=ChengdeItem(),response=response)
        chengde_loader.add_css("title",".house-title h1::text")
        chengde_loader.add_value("url",response.url)
        chengde_loader.add_value("url_object_id",get_md5(response.url))
        chengde_loader.add_css("rent_type",".house-basic-info  .house-basic-desc  ul > li:nth-child(1) > span:nth-child(2)::text")
        chengde_loader.add_css("price",".house-basic-info  .house-basic-desc  div  b::text")
        chengde_loader.add_css("hourse_type",".house-basic-info .house-basic-desc  ul > li:nth-child(2) > span:nth-child(2)::text")
        chengde_loader.add_css("area",".house-basic-info .house-basic-desc  ul > li:nth-child(5) > span:nth-child(2) > a:nth-child(1)::text")
        chengde_loader.add_css("community",".house-basic-info .house-basic-desc  ul > li:nth-child(4) > span:nth-child(2) > a::text")
        chengde_loader.add_value("detail",detail)
        chengde_loader.add_value("telephone",telephone)


        chengde_item = chengde_loader.load_item()
        yield chengde_item





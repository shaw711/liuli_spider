# -*- coding: utf-8 -*-
from traceback import format_exc

import scrapy
from scrapy.http import Request
# from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

from liuli_spider.items import LiuLiItemLoader,LiuLiItem
from liuli_spider.utils.common import get_md5
from pyquery import PyQuery as pq

'''
scrapy startproject ArticleSpider,创建项目
scrapy crawl jobbole ，创建爬虫  
start_urls是一个待爬的列表
scrapy shell http://blog.jobbole.com/110287/  ,  开启控制台调试
'''
class LiuliSpider(scrapy.Spider):
    name = 'liuli'
    allowed_domains = ['www.llss.cool']
    start_urls = ['http://www.llss.cool/wp/']

    #
    # handle_httpstatus_list = [404]
    # def __init__(self):
    #     self.fail_urls = []
    #     dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
    #
    # def handle_spider_closed(self,spider,reason):
    #     self.crawler.stats.set_value("failed_urls",",".join(self.fail_urls))



    def parse(self, response):
        # if response.status == 404:
        #     self.fail_urls.append(response.url)
        #     self.crawler.stats.inc_value("failed_url")
        '''#使用request下载详情页面，
        下载完成后回调方法parse_detail()提取文章内容中的字段 '''
        post_urls = response.css(".format-standard .entry-header .entry-title >a::attr(href)").extract()
        for post_url in post_urls:
            if post_url == "http://www.llss.cool/wp/all/game/2958/":
                pass
            else:
                yield Request(url=post_url,callback=self.parse_detail)

        next_url = response.css(".wp-pagenavi .nextpostslink ::attr(href)").extract_first("")
        if next_url:
            yield Request(url=next_url,callback=self.parse,
                          errback=self.error_back)

    def parse_detail(self,response):

        # if response.status == 404:
        #     self.fail_urls.append(response.url)
        #     self.crawler.stats.inc_value("failed_url")

        comment_nums = response.xpath("//*[@id='comments-title']/text()[2]").extract_first("default comments")
        average_score = response.css("center div > strong:nth-child(7)::text").extract_first("default score")
        # content = response.css("article> div > p::text").extract_first("新版")
        html = pq(response.text)
        content = html("article div p").text()

        '''实例化一个LiuLiItem，然后用LiuLiItemLoader给load进来
        itemloadr提供了一个容器，让我们配置某一个字段该使用哪种规则。
        add_css， add_value， add_xpath，'''
        item_loader = LiuLiItemLoader(item=LiuLiItem(),response=response)
        item_loader.add_css("title",".entry-title::text")
        item_loader.add_css("create_date", "header > div > a > time::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id",get_md5(response.url))
        item_loader.add_value("comment_nums",comment_nums )
        item_loader.add_value("average_score",average_score)
        item_loader.add_value("content",content)
        item_loader.add_css("tags", ".entry-meta a[rel$='tag']::text")
        article_item = item_loader.load_item()
        # print(article_item)

        yield article_item


    def error_back(self,e):
        _ = e
        self.logger.error(format_exc())



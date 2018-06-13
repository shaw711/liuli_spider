# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst,Join,MapCompose

from .models.es_types import ArticleType

'''确定服务器连接， 并创建一个实例'''
from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using)


'''此处的自定义方法一定要写在代码前面。'''
''' 2018年6月7日  2018-06-07'''
def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value,"%Y年%m月%d日").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date

def get_nums(value):
    #value = ",".join(value)
    if value == "":
        return 0
    else:
        match_re = re.match(".*?(\d+).*",value)
        if match_re:
            nums = int(match_re.group(1))
        else:
            nums = 0
        return nums


'''根据字符串生成搜索建议组 , set用于去重'''
def gen_suggests(index,info_tuple):
    used_words = set()
    suggests = []
    for text,weight in info_tuple:
        if text:
            words = es.indices.analyze(index=index, params={'filter':["lowercase"],"analyzer":"ik_max_word"},body=text)
            '''调用es的analyze接口分析字符串
            去处搜索建议，过滤单个字符'''
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1])
            '''把已经存在的词过滤掉'''
            new_words = anylyzed_words - used_words
        else:
            new_words = set()

        '''把值再传回suggest'''
        if new_words:
            suggests.append({"input":list(new_words),"weight":weight})

    return suggests

'''自定义itemloader实现默认提取第一个'''
class LiuLiItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

'''items 可以让我们自定义自己的字段（类似于字典，但比字典的功能更齐全）
   MapCompose可以传入函数对于该字段进行处理
'''
class LiuLiItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    comment_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
       # output_processor = MapCompose(return_value2)
    )
    average_score = scrapy.Field(
        # input_processor=MapCompose(get_nums2)
    )
    content = scrapy.Field(
        output_processor=Join(",")
    )
    tags = scrapy.Field(
        output_processor = Join(",")
    )

    '''items中添加get_insert_sql实现存入数据库'''
    def get_insert_sql(self):
        insert_sql = """
        insert into liuli_article(title,create_date,url,url_object_id,comment_nums,average_score,tags,content)
        values (%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE comment_nums=VALUES(comment_nums),
        average_score=VALUES(average_score),content=VALUES(content)
        """
        params = (self["title"],self["create_date"],self["url"],self["url_object_id"],self["comment_nums"],
                  self["average_score"],self["tags"],self["content"])

        return insert_sql,params

    '''items.py 中将数据保存至es'''
    def save_to_es(self):
        article = ArticleType()
        '''生成一个类实例'''
        article.title = self['title']
        article.create_date = self["create_date"]
        article.average_score = self["average_score"]
        article.comment_nums = self["comment_nums"]
        article.url = self["url"]
        article.tags = self["tags"]
        article.meta.id = self["url_object_id"]
        article.content = self["content"]

        '''搜索建议词，在插入时就要做处理，使用自定义的gen_suggests
        '''
        article.suggest = gen_suggests(ArticleType._doc_type.index,((article.title, 10), (article.tags, 7)))

        article.save()

        #redis_cli.incr("jobbole_count")

        return




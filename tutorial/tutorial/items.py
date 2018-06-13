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

from .models.es_types import ChengdeType

'''返回原值'''
def return_value2(value):
    return value

'''以换行符分割'''
def mk_detail(value):
    result = value.split('\n')
    return result

'''以空格分隔'''
def mk_hourse_type(value):
    result = value.split()
    return result

'''确定服务器连接， 并创建一个实例'''
from elasticsearch_dsl.connections import connections
es = connections.create_connection(ChengdeType._doc_type.using)


''' 转化日期 ，2018年6月7日 ，2018-06-07'''
def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value,"%Y年%m月%d日").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date

'''获取文字中的数字'''
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


'''自定义itemloader'''
'''实现默认提取第一个'''
class ChengdeItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class ChengdeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    '''这个词不需要分词'''
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    rent_type = scrapy.Field()
    price = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    hourse_type = scrapy.Field(
        input_processor=MapCompose(mk_hourse_type),
        output_processor=Join(",")
    )
    area = scrapy.Field()
    community = scrapy.Field()
    detail = scrapy.Field(
        input_processor=MapCompose(mk_detail),
        output_processor = Join(",")

    )
    telephone = scrapy.Field()

    '''items中添加get_insert_sql实现存入数据库'''
    def get_insert_sql(self):
        insert_sql = """
           insert into liuli_article(title,create_date,url,url_object_id,comment_nums,average_score,tags,content)
           values (%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE comment_nums=VALUES(comment_nums),
           average_score=VALUES(average_score),content=VALUES(content)
           """
        params = (self["title"], self["create_date"], self["url"], self["url_object_id"], self["comment_nums"],
                  self["average_score"], self["tags"], self["content"])

        return insert_sql, params


    '''items.py 中将数据保存至es'''
    def save_to_es(self):
        article = ChengdeType()
        '''生成一个类实例'''
        article.title = self['title']
        article.url = self["url"]
        article.meta.id = self["url_object_id"]
        article.rent_type = self["rent_type"]
        article.price = self["price"]
        article.hourse_type = self["hourse_type"]
        article.area = self["area"]
        article.community = self["community"]
        article.detail = self["detail"]
        article.telephone = self["telephone"]



        '''搜索建议词，在插入时就要做处理，使用自定义的gen_suggests'''
        article.suggest = gen_suggests(ChengdeType._doc_type.index, ((article.title, 10), (article.hourse_type, 7)))
        article.save()
        return



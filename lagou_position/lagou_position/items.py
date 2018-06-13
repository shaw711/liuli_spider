# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst,Join,Compose,MapCompose
import time
import datetime
from .models.es_types import LagouType

'''确定服务器连接， 并创建一个实例'''
from elasticsearch_dsl.connections import connections
es = connections.create_connection(LagouType._doc_type.using)

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

def date_convert(value):
    if '今天' in value:
        return datetime.date.today()

    # 昨天时间

    elif '昨天' in value:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        return yesterday

def split_join(value):
    value = value.split()
    return value


class LagouLoader(ItemLoader):
    default_output_processor = TakeFirst()

class LagouPositionItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    positionName = Field()
    companyName = Field()
    companyFullName = Field()
    createTime = Field(
        input_processor=MapCompose(date_convert)
    )
    salary = Field()
    work_time = Field()
    education = Field(
        input_processor=MapCompose(split_join),
        output_processor=Join(",")
    )
    locals = Field()
    work_description = Field(
        output_processor=Join(",")
    )
    company_description = Field(
        input_processor=MapCompose(split_join),
        output_processor = Join(",")
    )
    url = Field()
    url_object_id = Field()


    '''items.py 中将数据保存至es'''
    def save_to_es(self):
        article = LagouType()
        '''生成一个类实例'''
        article.positionName = self['positionName']
        article.companyName = self["companyName"]
        article.companyFullName = self["companyFullName"]
        # article.createTime = self["createTime"]
        article.salary = self["salary"]
        article.work_time = self["work_time"]
        article.education = self["education"]
        article.locals = self["locals"]
        article.work_description = self["work_description"]
        article.company_description = self["company_description"]
        article.url = self["url"]
        article.meta.id = self["url_object_id"]

        '''搜索建议词，在插入时就要做处理，使用自定义的gen_suggests
        '''
        article.suggest = gen_suggests(LagouType._doc_type.index,((article.positionName, 10), (article.company_description, 7)))
        article.save()

        #redis_cli.incr("jobbole_count")

        return


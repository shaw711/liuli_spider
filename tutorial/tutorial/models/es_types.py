# -*- coding:utf-8 -*-
__author__ = 'mangu'
__date__ = '2018/2/21 12:02'

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text,Integer

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer


'''确定服务器连接'''
from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

'''定义一个分析器  ，lowercase 大小写转换'''
ik_analyzer = CustomAnalyzer("ik_max_word",filter=["lowercase"])


'''参考了django的model ， 定义els中的type'''
class ArticleType(DocType):
    # 伯乐在线文章类型
    # 搜索建议自动补全 ，设置Completion类型 ， 目前要用自定义的CustomAnalyzer避免报错
    suggest = Completion(analyzer=ik_analyzer)
    '''搜索时需要进行分词'''
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    '''这个词不需要分词'''
    url = Keyword()
    url_object_id = Keyword()
    comment_nums = Integer()
    average_score = Keyword()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    """
    liuli1的
    content是keyword
    """

    '''确定目标保存的 index和type'''
    class Meta:
        index = "liuli1"
        doc_type = "article"


class ChengdeType(DocType):
    # 伯乐在线文章类型
    '''搜索时需要进行分词'''
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    '''这个词不需要分词'''
    url = Keyword()
    url_object_id = Keyword()
    rent_type = Keyword
    price = Integer()
    hourse_type = Keyword()
    area = Text(analyzer="ik_max_word")
    community = Text(analyzer="ik_max_word")
    detail = Text(analyzer="ik_max_word")
    telephone = Keyword()
    """
    liuli1的
    content是keyword
    """

    '''确定目标保存的 index和type'''
    class Meta:
        index = "zufang"
        doc_type = "chengde58"

''' 根据类中的init方法在els中直接生成mapping映射'''
if __name__ == "__main__":
    ChengdeType.init()
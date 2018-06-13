# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


'''把爬取的数据保存至elasticsearch'''
class ElasticsearchPipeline(object):

    def process_item(self, item, spider):
        #将item转换为es的数据
        item.save_to_es()

        return item

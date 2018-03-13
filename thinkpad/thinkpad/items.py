# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ThinkpadItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class PerksOfferWeeklySaleItem(scrapy.Item):
    end_date = scrapy.Field()       #结束时间
    model = scrapy.Field()          #型号
    save_up = scrapy.Field()        #降价比例

class PerksOfferMonthlySaleItem(scrapy.Item):
    model = scrapy.Field()          #型号
    save_up = scrapy.Field()        #降价比例

class PerksOfferConsumerSaleItem(scrapy.Item):
    end_date = scrapy.Field()       #结束时间
    model = scrapy.Field()          #型号
    save_up = scrapy.Field()        #降价比例

class PerksOfferClearanceSaleItem(scrapy.Item):
    model = scrapy.Field()          #型号
    save_up = scrapy.Field()        #降价比例

class PerksOfferProductItem(scrapy.Item):
    model = scrapy.Field()          #型号
    starting_price = scrapy.Field() #起始价格

class OutletProductItem(scrapy.Item):
    model = scrapy.Field()  #型号
    price = scrapy.Field()  #价格
    status = scrapy.Field() #状态
    configuration = scrapy.Field() #配置

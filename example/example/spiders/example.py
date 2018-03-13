# -*- coding: utf-8 -*-
import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'example'
    start_urls = ['http://woodenrobot.me']

    def parse(self, response):
        print type(response),response
        titles = response.xpath('//a[@class="post-title-link"]/text()').extract()
        for title in titles:
            print title.strip()

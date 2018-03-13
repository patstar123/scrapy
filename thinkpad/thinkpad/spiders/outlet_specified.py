# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.spiders import Spider
from thinkpad.items import OutletProductItem
import thinkpad.thinkpad_defs as tp

specified_products = [
    '14in', '15in'
]

pass_filters = [
    't470p', 'p50', 'p51'
]

reject_filters = [
    "p51s", "p50s"
]

cfg_pass_filters = [
    "Intel", "Windows", "Memory", "Drive"
]

class OutletSpecifiedSpider(Spider):
    name = 'outlet_specified'
    allowed_domains = [tp.domain]

    def close(self, reason):
        tp.notify_user('Lenovo Outlet Specified', self.name, self)

    def start_requests(self):
        self.product_index = 0
        login_request = tp.login_request
        login_request.callback = self.ok_outlet_login
        return [login_request]

    def ok_outlet_login(self, response):
        req = self.get_next_request(None)
        if req is not None:
            yield req

    def get_next_request(self, response):
        if response is not None:
            next_page_url = self.get_next_page_url(response)
            if next_page_url is not None:
                return Request(next_page_url, headers = tp.http_headers, callback = self.on_response)

        if self.product_index >= len(specified_products):
            return None
        self.product_name = specified_products[self.product_index]
        self.product_index += 1
        return Request(
            tp.request_urls[self.name + '_' + self.product_name], 
            headers = tp.http_headers,
            callback = self.on_response)

    def on_response(self, response):
        for product in self.get_outlet_specified_products(response):
            yield product
        yield self.get_next_request(response)

    def get_outlet_specified_products(self, response):
        results_keys = [
            ('//div', None, 'mainContent contentContainer pageWrapper '),
            ('//div', 'id', 'results-area'),
            ('//div', 'id', 'resultsList'),
            ('//div', None, 'facetedResults-item only-allow-small-pricingSummary'),
        ]
        results_pattern = tp.fast_gen_pattern2(results_keys)
        results = response.xpath(results_pattern)

        name_keys = [
            ('.//div' , None, 'facetedResults-header'),
            ('//h3'   , None, 'facetedResults-title' ),
            ('//a'    , None, 'facetedResults-cta'   ),
            ('/text()', None, None                   ),
        ]
        name_pattern = tp.fast_gen_pattern2(name_keys)

        price_keys = [
            ('.//div' , None, 'facetedResults-body'),
            ('//div', None, 'pricingSummary'),
            ('//dd', None, 'pricingSummary-details-final-price'),
            ('/text()', None, None)
        ]
        price_pattern = tp.fast_gen_pattern2(price_keys)

        status_keys = [
            ('.//div' , None, 'facetedResults-body'),
            ('//div', None, 'pricingSummary'),
            ('//div', None, 'pricingSummary-secondary-details'),
            ('//span', None, 'rci-msg'),
            ('/text()', None, None),
        ]
        status_pattern = tp.fast_gen_pattern2(status_keys)
        
        configurations_keys = [
            ('.//div' , None, 'facetedResults-body'),
            ('//div', None, 'facetedResults-feature-list'),
            ('//dd', None, None),
            ('/text()', None, None),
        ]
        configurations_pattern = tp.fast_gen_pattern2(configurations_keys)
        
        products = []
        for item in results:
            try:
                name = item.xpath(name_pattern).extract()[0]
                status = item.xpath(status_pattern).extract()[0]
                price = item.xpath(price_pattern).extract()[0]
                price = tp.check_price('price', price)
            except IndexError as e:
                self.logger.error('!!! invalid product detail: ' + item.extract())
                continue
            
            name = tp.check_name(name, pass_filters, reject_filters, False)
            if name is None:
                continue
            if not tp.price_is_within_limits(price):
                continue

            configurations = item.xpath(configurations_pattern).extract()
            configuration = ''
            for cfg in configurations:
                cfg = tp.strip_invisible_chars(cfg)
                if not tp.is_in_filters(cfg_pass_filters, cfg, False):
                    continue
                if len(cfg) > 0:
                    configuration += cfg + '\t'
            configuration = configuration[:-1]
        
            product = OutletProductItem()
            product['model'] = name
            product['price'] = price
            product['status'] = tp.strip_invisible_chars(status)
            product['configuration'] = configuration
            products.append(product)

        return products

    def get_next_page_url(self, response):
        next_page_keys = [
            ('//div', None, 'mainContent contentContainer pageWrapper '),
            ('//div', 'id', 'results-area'),
            ('//div', None, 'paginationBar top clearfix'),
            ('//div', None, 'right'),
            ('//a', 'rel', 'next'),
            ('[contains(text(),"Next Page")]', None, None),
            ('/@href', None, None)
        ]
        next_page_pattern = tp.fast_gen_pattern2(next_page_keys)
        next_page = response.xpath(next_page_pattern).extract()
        if len(next_page) > 0:
            return tp.web_host + next_page[0]
        else:
            return None
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)

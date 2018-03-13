# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.spiders import Spider
from thinkpad.items import PerksOfferProductItem
import thinkpad.thinkpad_defs as tp

specified_products = [
    't470p', 'p50', 'p51'
]

class PerksOfferSpecifiedSpider(Spider):
    name = 'perksoffer_specified'
    allowed_domains = [tp.domain]

    def close(self, reason):
        tp.notify_user('Perks Offer Specified', self.name, self)

    def start_requests(self):
        self.product_index = 0
        login_request = tp.login_request
        login_request.callback = self.ok_perksoffer_login
        return [login_request]

    def ok_perksoffer_login(self, response):
        req = self.get_next_request()
        if req is not None:
            yield req

    def get_next_request(self):
        if self.product_index >= len(specified_products):
            return None
        self.product_name = specified_products[self.product_index]
        self.product_index += 1
        return Request(
            tp.request_urls[self.name + '_' + self.product_name], 
            headers = tp.http_headers,
            callback = self.on_response)

    def on_response(self, response):
        yield self.get_perksoffer_specified_product(response)
        yield self.get_next_request()

    def get_perksoffer_specified_product(self, response):

        price_keys = [
            ('//div'  , None      , 'mainContent contentContainer pageWrapper ',),
            ('//div'  , 'id'      , 'longscroll-subseries',                     ),
            ('//div'  , None      , 'hero-column hero-column-one',              ),
            ('//div'  , None      , 'cta',                                      ),
            ('//dl'   , None      , 'cta-price',                                ),
            ('//dd'   , 'itemprop', 'price',                                    ),
            ('/text()', None      , None                                        ),
        ]
        price_pattern = tp.fast_gen_pattern2(price_keys)
        price = response.xpath(price_pattern).extract()
        price = tp.check_price('starting price', price)

        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        product = PerksOfferProductItem()
        product['model'] = self.product_name
        product['starting_price'] = price
        return product

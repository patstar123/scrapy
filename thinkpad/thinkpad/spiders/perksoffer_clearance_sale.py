# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.spiders import Spider
from thinkpad.items import PerksOfferClearanceSaleItem
import thinkpad.thinkpad_defs as tp

pass_filters = [
    "thinkpad"
]

class PerksOfferClearanceSaleSpider(Spider):
    name = 'perksoffer_clearance_sale'
    allowed_domains = [tp.domain]

    def close(self, reason):
        tp.notify_user('Perks Offer Clearance Sale', self.name, self)

    def start_requests(self):
        login_request = tp.login_request
        login_request.callback = self.ok_perksoffer_login
        return [login_request]

    def ok_perksoffer_login(self, response):
        yield Request(
            tp.request_urls[self.name], 
            headers = tp.http_headers,
            callback = self.ok_perksoffer_clearance_sale)

    def ok_perksoffer_clearance_sale(self, response):
        for product in self.get_perksoffer_clearance_sale_in_detail(response):
            yield product

    def get_perksoffer_clearance_sale_in_detail(self, response):

        products_k1s = ['//div', '//ul', '//li']
        products_k2s = ['weeklyDealsContainer', 'non-featured-products', 'product-column v[filters]']
        products_k3s = ['id', None, None]
        products_pattern = tp.fast_gen_pattern(products_k1s, products_k2s, products_k3s)
        non_featured_products = response.xpath(products_pattern)

        name_k1s = ['.//div', '//h4', '/text()']
        name_k2s = ['product-title qa_modelName', None, None]
        name_pattern = tp.fast_gen_pattern(name_k1s, name_k2s)
        web_price_k1s = ['.//div', '//div', '//div', '//dd', '/text()']
        web_price_k2s = ['pricing', 'price-block', 'webprice qa_webPrice', 'webprice-final', None]
        web_price_pattern = tp.fast_gen_pattern(web_price_k1s, web_price_k2s)
        saving_price_k1s = ['.//div', '//div', '//div', '//span', '/text()']
        saving_price_k2s = ['pricing', 'price-block', 'yousave-section qa_savings', 'yousave qa_savingsPrice', None]
        saving_price_pattern = tp.fast_gen_pattern(saving_price_k1s, saving_price_k2s)

        products = []
        for non_featured_product in non_featured_products:
            name = non_featured_product.xpath(name_pattern).extract()
            name = tp.check_name(name, pass_filters, None, False)
            if name is None:
                continue
            web_price = non_featured_product.xpath(web_price_pattern).extract()
            saving_price = non_featured_product.xpath(saving_price_pattern).extract()
            web_price = tp.check_price('web price', web_price)
            saving_price = tp.check_price('saving price', saving_price)
            discount = 0
            if web_price > 0.0:
                discount = int(round((saving_price / web_price) * 100))
            product = PerksOfferClearanceSaleItem()
            product['model'] = name
            product['save_up'] = str(discount) + '%'
            products.append(product)

        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        return products

# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.spiders import Spider
from thinkpad.items import PerksOfferWeeklySaleItem
import thinkpad.thinkpad_defs as tp

pass_filters = [
    "t470p", "p51", "p50"
]

reject_filters = [
    "p51s", "p50s"
]

class PerksOfferWeeklySaleSpider(Spider):
    name = 'perksoffer_weekly_sale'
    allowed_domains = [tp.domain]

    def close(self, reason):
        tp.notify_user('Lenovo Perks Offer Weekly Sale', self.name, self)

    def start_requests(self):
        login_request = tp.login_request
        login_request.callback = self.ok_perksoffer_login
        return [login_request]

    def ok_perksoffer_login(self, response):
        yield Request(
            tp.request_urls[self.name], 
            headers = tp.http_headers,
            callback = self.ok_perksoffer_weekly_sale)

    def ok_perksoffer_weekly_sale(self, response):
        self.end_date = self.get_perksoffer_weekly_sale_end_date(response)
        for product in self.get_perksoffer_weekly_sale_in_detail(response):
            yield product

    def get_perksoffer_weekly_sale_end_date(self, response):
        fixed_end_time = 'at 4AM EST'
        scripts = response.xpath('//script/text()')
        pattern = "$('#endDate').text('"
        end_date = '-'
        for s in scripts:
            ss = s.extract()
            idx = ss.find(pattern)
            if idx == -1:
                continue
            ss = ss[idx + len(pattern):]
            end_date = ss[:ss.find("'")]
        end_date += ' ' + fixed_end_time
        return end_date

    def get_perksoffer_weekly_sale_in_detail(self, response):
        name_key1s = ['//div', '//h4', '/text()']
        name_key2s = ['product-title qa_modelName', None, None]
        name_pattern = tp.fast_gen_pattern(name_key1s, name_key2s)
        names = response.xpath(name_pattern).extract()

        pricing_summary_key1s = ['//div', '//dl']
        pricing_summary_key2s = ['pricing', 'pricingSummary-details']
        pricing_summary_pattern = tp.fast_gen_pattern(pricing_summary_key1s, pricing_summary_key2s)
        pricing_summarys = response.xpath(pricing_summary_pattern)

        if len(names) != len(pricing_summarys):
            raise ValueError('logical error: pricingSummarys do not relate with model names')

        web_price_key1s = ['.//div', '//div', '//dd', '/text()']
        web_price_key2s = ['price-block', 'webprice qa_webPrice', 'webprice-final', None]
        web_price_pattern = tp.fast_gen_pattern(web_price_key1s, web_price_key2s)
        saving_price_key1s = ['.//div', '//div', '//span', '/text()']
        saving_price_key2s = ['price-block', 'yousave-section qa_savings', 'yousave qa_savingsPrice', None]
        saving_price_pattern = tp.fast_gen_pattern(saving_price_key1s, saving_price_key2s)

        products = []
        for name, pricing_summary in zip(names, pricing_summarys):
            name = tp.check_name(name, pass_filters, reject_filters, False)
            if name is None:
                continue

            web_price = pricing_summary.xpath(web_price_pattern).extract()
            saving_price = pricing_summary.xpath(saving_price_pattern).extract()
            web_price = tp.check_price('web price', web_price)
            saving_price = tp.check_price('saving price', saving_price)
            discount = 0
            if web_price > 0.0:
                discount = int(round((saving_price / web_price) * 100))
            product = PerksOfferWeeklySaleItem()
            product['end_date'] = self.end_date
            product['model'] = name
            product['save_up'] = str(discount) + '%'
            products.append(product)

        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        return products

    '''
    def get_perksoffer_weekly_sale_in_detail2(self, response):
        products = []

        product_pattern_tree = {
            'type': None,
            'featured-product': {
                'type': '//div',
                'product-title qa_modelName': {
                    'type': '//div',
                    '': {
                        'type': '//h4',
                        '': {
                            'type': '/text()',
                            'name': 'product_name'
                        }
                    }
                },
                'price-block': {
                    'type': '//div',
                    'webprice qa_webPrice': {
                        'type': '//div',
                        'webprice-final': {
                            'type': '//dd',
                            '': {
                                'type': '/text()',
                                'name': 'web_price'
                            }
                        }
                    },
                    'yousave-section qa_savings': {
                        'type': '//div',
                        'yousave qa_savingsPrice': {
                            'type': '//span',
                            '': {
                                'type': '/text()',
                                'name': 'saving_price'
                            }
                        }
                    }
                }
            },
        }
        patterns = {}
        self.gen_xpath_patterns(None, product_pattern_tree, '', patterns)
        print patterns
        return products

    def gen_xpath_patterns(self, name, trees, prefix, patterns):
        if not trees.has_key('type'):
            raise ValueError('invalid trees: ' + trees)

        type_s = trees.get('type')
        if type_s is not None:
            prefix += type_s
        if name is not None and name != '':
            prefix += '[@class="%s"]' % name

        keys = trees.keys()
        if 'name' in keys:
            patterns[trees.get('name')] = prefix

        for item in keys:
            if item in ['type', 'name']:
                continue
            self.gen_xpath_patterns(item, trees.get(item), prefix, patterns)

    '''

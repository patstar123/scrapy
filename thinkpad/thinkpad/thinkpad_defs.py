# -*- coding: utf-8 -*-
import scrapy
import filecmp, os, time
from scrapy.mail import MailSender

out_to_email = False

price_min = 900
price_max = 1700

domain = 'www3.lenovo.com'

web_host = 'https://www3.lenovo.com'

request_urls = {
    'perksoffer_login': 'https://www3.lenovo.com/us/en/perksoffer/gatekeeper/authGatekeeper',
    'perksoffer_weekly_sale': 'https://www3.lenovo.com/us/en/perksoffer/landingpage/promotions/weekly-sale/thinkpad-laptops',
    'perksoffer_monthly_sale': 'https://www3.lenovo.com/us/en/perksoffer/landingpage/promotions/affinity-monthly-sale/',
    'perksoffer_consumer_sale': 'https://www3.lenovo.com/us/en/perksoffer/landingpage/consumer-sale/',
    'perksoffer_clearance_sale': 'https://www3.lenovo.com/us/en/perksoffer/landingpage/promotions/lenovo-clearance-sale/',
    'perksoffer_specified_t470p': 'https://www3.lenovo.com/us/en/perksoffer/laptops/thinkpad/thinkpad-t-series/ThinkPad-T470p/p/22TP2TT470P',
    'perksoffer_specified_p50': 'https://www3.lenovo.com/us/en/perksoffer/laptops/thinkpad/thinkpad-p/ThinkPad-P50/p/22TP2WPWP50',
    'perksoffer_specified_p51': 'https://www3.lenovo.com/us/en/perksoffer/laptops/thinkpad/thinkpad-p/P51/p/22TP2WPWP51',
    'outlet_specified_14in': 'https://www3.lenovo.com/us/en/outletus/laptops/c/LAPTOPS?q=%3Aprice-asc%3AfacetSys-Processor%3AIntel%C2%AE+Core%E2%84%A2+i7%3AfacetSys-ScreenSize%3A14+in%3AfacetSys-Memory%3A16GB%3AfacetSys-HardDrive%3A512GB+Solid+State&uq=&text=#',
    'outlet_specified_15in': 'https://www3.lenovo.com/us/en/outletus/laptops/c/LAPTOPS?q=%3Aprice-asc%3AfacetSys-Processor%3AIntel%C2%AE+Core%E2%84%A2+i7%3AfacetSys-Processor%3AIntel%C2%AE+Xeon%C2%AE%3AfacetSys-ScreenSize%3A15.6+in%3AfacetSys-Memory%3A16GB%3AfacetSys-Memory%3A32GB&uq=&text=#',
}

http_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
}

login_request = scrapy.FormRequest(
    request_urls['perksoffer_login'],
    headers = http_headers,
    formdata = {
        'gatekeeperType': 'PasscodeGatekeeper',
        'passcode': 'NJ*PERKSEPP',
        'CSRFToken': '1b850052-c713-4f36-936d-b6320ee9f238'})

def strip_invisible_chars(chars):
    return chars.replace('\r', '').replace('\n', '').replace('\t', '').strip()

def check_name(names, pass_filters, reject_filters, is_strict):
    if isinstance(names, list):
        if len(names) == 0:
            return None
        else:
            names = names[0]
    if pass_filters is not None and not is_in_filters(pass_filters, names, is_strict):
        return None 
    if reject_filters is not None and is_in_filters(reject_filters, names, is_strict):
        return None 
    return names

def check_price(name, prices):
    if not isinstance(prices, list):
        prices = [prices]
    if len(prices) == 0:
        return 0.0
    elif len(prices) > 1:
        raise ValueError('logical error: there is more then one %s[%s] for %s' % (name, prices, name))
    else:
        return float(prices[0].replace('$', '').replace(',', '').strip())

def price_is_within_limits(price):
    return (price < price_max and price > price_min)

def fast_gen_pattern(key1s, key2s, key3s=None):
    if key3s is None:
        key3s = [None] * len(key1s)
    pattern = ''
    for k1, k2, k3 in zip(key1s, key2s, key3s):
        pattern += k1
        if k2 is not None:
            if k3 is None: k3 = 'class'
            pattern += '[@%s="%s"]' % (k3, k2)
    return pattern

def fast_gen_pattern2(keys):
    '''k1(div), k2(class), k3(xxx)'''
    pattern = ''
    for k1, k2, k3 in keys:
        pattern += k1
        if k3 is not None:
            if k2 is None: k2 = 'class'
            pattern += '[@%s="%s"]' % (k2, k3)
    return pattern

def is_in_filters(filters, src, is_strict):
    for flr in filters:
        if flr == '' or flr == '*':
            return True
        if is_strict:
            if src.startswith(flr):
                return True
        else:
            if src.lower().find(flr.lower()) != -1:
                return True
    return False

def notify_user(title, spider_name, spider=None):
    if not out_to_email:
        if spider is not None: spider.logger.warning("out_to_email is False")
        return
    
    cur_file = spider_name + '.csv'
    last_file = 'last_' + cur_file

    if not is_need_notify(last_file, cur_file):
        if spider is not None: spider.logger.warning("No need to notify user")
        return

    mailer = MailSender(  
        smtphost = "smtp.qq.com",        # 发送邮件的服务器  
        mailfrom = "xxxxxxxxx@qq.com",   # 邮件发送者  
        smtpuser = "xxxxxxxxx@qq.com",   # 用户名  
        smtppass = "xxxxxxxxxxxxxxxx",   # 授权码
        smtpport = 25                    # 端口号 25 ssl 465/587
    )  

    subject = '[%s]%s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), title)
    
    timestamp = time.strftime("%m%d%H%M%S", time.localtime())

    body = 'Scrapy auto sends'

    attachs = [
        (spider_name + '_' + timestamp + '.csv', 'text/comma-separated-values', file(cur_file, 'r'))
    ]

    mailer.send(
        to = ["xxxxxxxxx@qq.com"], 
        subject = subject, 
        body = body,
        attachs = attachs)

def is_need_notify(f1, f2):
    if not os.path.exists(f1) or not os.path.exists(f2):
        return True
    if not filecmp.cmp(f1, f2):
        return True
    day1 = time.strftime("%m%d", time.localtime(os.path.getmtime(f1)))
    day2 = time.strftime("%m%d", time.localtime(os.path.getmtime(f2)))
    if day1 != day2:
        return True
    return False
    
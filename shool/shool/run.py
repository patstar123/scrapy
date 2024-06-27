# -*- coding: utf-8 -*-

from scrapy import cmdline

cmd = 'scrapy crawl douban_movie_top250 -o douban.csv'
cmdline.execute(cmd.split())
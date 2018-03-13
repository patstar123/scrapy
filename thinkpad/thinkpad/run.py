# -*- coding: utf-8 -*-

from scrapy import cmdline

cmd = 'scrapy crawl outlet_specified -o outlet_specified.csv -L INFO' # --nolog
cmdline.execute(cmd.split())
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import re
import time
from sendmail import send_mail
from common import read_html, traverse_html, AssistThread


yihaodian_url = 'http://www.yihaodian.com|http://www.1mall.com/'
yihaodian_item_url = 'http://www.(?:yihaodian|1mall).com/item/(?:\d+)_\d'
#1mall_item_url = '^http://www.1mall.com/item/(?:\d+)_\d'
#1haodian_items_url = '^http://www.yihaodian.com/ctg/|^http://www.yihaodian.com/channel/(?:\d+)_\d(?:/)?$'
yihaodian_items_pt = 'href=\"(http://www.(?:yihaodian|1mall).com/item/(\d+)_\d)[\"\?/].*title\=\"([^\"]+)\"'
yihaodian_re = re.compile(yihaodian_url)
yihaodian_item_re = re.compile(yihaodian_item_url)
yihaodian_items_re = re.compile(yihaodian_items_pt)
#1mall_item_re = re.compile(1mall_item_url)


headers = {'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)'}

product_title_re = re.compile('<input .* id=\"productName\".*value=\"(.+)\"')
pmid_re = re.compile('^http://www.(?:yihaodian|1mall).com/item/(\d+)_\d')

details_re = re.compile('\"currentPrice\":([\d\.]+).*\"marketPrice\":([\d\.]+).*\"yhdPrice\":([\d\.]+).*\"promPrice\":([\d\.]+).*\"currentStockNum\":([\d]+).*\"remainTime\":([\d]+)')

ajax_url = 'http://busystock.i.yihaodian.com/restful/detail?mcsite=1&provinceId=6&pmId=%s'


class YihaodianThread(AssistThread):

    def __init__(self, queue, url, price, title):
        AssistThread.__init__(queue)
        self.url = url
        self.price = price
        self.title = title

    def process_job():
        html = read_html(self.url)
        self.title = product_title_re.search(html).group(0)
        print self.title, self.price

def YihaodianThreadFactory(threading.Thread):

    def __init__(self, queue, url, price):
        threading.Thread.__init__()
        self.queue = queue
        self.url = url
        self.price = price

    def run(self):
        html = read_html(self.url)
        item = yihaodian_item_re.search(self.url)
        if item:
            pmid = item.group(0)
            title = product_title_re.search(html).group(0)
            if self.price == 0:
                self.price = int(details_re.search(read_html(ajax_url % pmid)).group(0))
            YihaodianThread(self.queue, self.url, self.price, title).start()
        else:
            for item in traverse_html(html, yihaodian_items_pt):
                YihaodianThread(self.queue, item[0], item[1], item[2]).start()


def check_waiting_list(waitings):
    for url, info in waitings.iteritems():
        if info['hit'] < -10:
            info['hit'] += 1
            continue
        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        the_page = response.read()
        product_name = re_product_name.search(the_page).group(1)
        pm_id = re_pm_id.search(the_page).group(1)

        #print product_name, pm_id
        req = urllib2.Request(ajax_url % pm_id, headers=headers)
        response = urllib2.urlopen(req)
        json = response.read()

        details = re_details.search(json)
        curr_price = float(details.group(1))
        market_price = float(details.group(2))
        yhd_price = float(details.group(3))
        prom_price = float(details.group(4))
        stock_num = int(details.group(5))
        remain_time = int(details.group(6)) // 1000

        #print curr_price, ops
        subject = '%s 当前价格%0.2f元，库存%d件, 剩余时间%d时%d分' % \
            (product_name, curr_price, stock_num, remain_time/3600, (remain_time % 3600) // 60)
        content = '%s  %s' % (subject, url)
        print subject

        if info['price'] == 0:
            if info['hit'] >= 0:
                info['price'] = curr_price
                print 'update product price'
            else:
                info['hit'] += 1
        elif curr_price < info['price']:
            if info['hit'] >= 5:
                if send_mail(subject, content):
                    print '发送通知成功 %s' % subject
                    info['hit'] = -1000
                else:
                    print '发送通知失败 %s' % subject
            else:
                info['hit'] += 1
                info['update'] = time.time()
        elif time.time() - info['update'] > 120.0:
            info['hit'] = 0
        time.sleep(10)

def url_waiting_list(file_path = './waiting.txt'):
    lists = open(file_path, 'r')
    entry = lists.readline().strip()
    while entry:
        if len(entry) > 2 and entry[0] != '#':
            e = entry.split(' ')
            yield e[0], int(e[1]) if len(e) > 1 else 0
        entry = lists.readline().strip()
    lists.close()

if __name__ == '__main__':
    #assert(yihaodian_re.match('http://www.1mall.com/2/'))
    #assert(yihaodian_re.match('http://www.yihaodian.com/2/?type=3'))
    #assert(not yihaodian_item_re.match('http://www.yihaodian.com/2/?type=3'))
    #assert(yihaodian_item_re.match('http://www.yihaodian.com/item/995742_2?ref=1_1_44_search.promotion_1'))
    #assert(yihaodian_item_re.match('http://www.1mall.com/item/995742_2?ref=1_1_44_search.promotion_1'))
    #assert(yihaodian_item_re.match('http://www.1mall.com/item/8880977_1'))
    #assert(yihaodian_item_re.match('http://www.yihaodian.com/item/995742_2'))
    #assert(yihaodian_item_re.match('http://www.yihaodian.com/item/995742_2/'))
    #assert(yihaodian_item_re.match('http://www.yihaodian.com/item/995742_2?'))

    pass
#    waitings = dict()
#    for u, p in url_waiting_list():
#        waitings[u] = p
#    while True:
#        check_waiting_list(waitings)
#        time.sleep(200)




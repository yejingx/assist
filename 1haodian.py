#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import re
import time
from sendmail import send_mail



item_pattern = 'pmId=\"(\d+)\" href=\"(http://www.yihaodian.com/item/(\d+)_\d\?[^\";\'\)]*)\".*title\=\"([^\"]+)\"'
item_re = re.compile(item_pattern)


headers = {'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)'}

re_product_name = re.compile('<input .* id=\"productName\".*value=\"(.+)\"')
re_pm_id        = re.compile('<input .* id=\"productMercantId\".*value=\"(.+)\"')

re_details = re.compile('\"currentPrice\":([\d\.]+).*\"marketPrice\":([\d\.]+).*\"yhdPrice\":([\d\.]+).*\"promPrice\":([\d\.]+).*\"currentStockNum\":([\d]+).*\"remainTime\":([\d]+)')

ajax_url = 'http://busystock.i.yihaodian.com/restful/detail?mcsite=1&provinceId=6&pmId=%s'

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

def url_waiting_list():
    lists = open('./waiting.txt', 'r')
    entry = lists.readline().strip()
    while entry:
        if len(entry) > 2:
            e = entry.split(' ')
            p = int(e[1]) if len(e) > 1 else 0
            yield e[0], {'price':p, 'hit':-5, 'update':time.time()}
        entry = lists.readline().strip()
    lists.close()

if __name__ == '__main__':
    waitings = dict()
    for u, p in url_waiting_list():
        waitings[u] = p
    while True:
        check_waiting_list(waitings)
        time.sleep(200)




#!/usr/bin/env python
# encoding=utf-8


import re
import urllib2

headers = {'User-Agent' : 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31'}
#headers = {'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)'}
#headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27'}
def read_html(url, headers = headers):
    req = urllib2.Request(url, headers = headers)
    response = urllib2.urlopen(req)
    the_page = response.read()
    return the_page

def traverse_html(html, pattern):
    url_pattern = re.compile(pattern)
    urls = re.findall(url_pattern, html)
    return set(urls)


if __name__ == '__main__':
    #traverse_html('', 'str')
    #traverse_html('', ('str', 1))
    #traverse_html('', 1)
    #print read_html('http://www.yihaodian.com/item/1262914_2')
    #ajax_url = 'http://busystock.i.yihaodian.com/restful/detail?mcsite=1&provinceId=6&pmId=1262914'
    #print read_html(ajax_url)
    html = read_html('http://www.yihaodian.com/ctg/s2/c5266-%E5%9D%9A%E6%9E%9C/')
    #open('./html.txt', 'w').write(html)
    #pattern = 'pmId=\"(\d+)\" href=\"(http://www.yihaodian.com/item/(\d+)_\d\?[^\";\'\)]*)\".*title=\'([^\"]+)\"'
    pattern = 'pmId=\"(\d+)\" href=\"(http://www.yihaodian.com/item/(\d+)_\d\?[^\";\'\)]*)\".*title\=\"([^\"]+)\"'
    #pattern = '(http://www.yihaodian.com/item/(\d+)_\d\?[^\";\'\)]*)'
    urls = traverse_html(html, pattern)
    for url in urls:
        print url[3]



    pass

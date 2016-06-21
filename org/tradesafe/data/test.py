# coding: utf-8
'''
Created on 2016年6月19日

@author: tack
'''
from urllib2 import Request, urlopen

import tushare

from org.tradesafe.data.history_data import HistoryData
import json
import demjson

if __name__ == '__main__':
    hd = HistoryData('/home/tack/stock')
    import sys

    reload(sys)

#     sys.setdefaultencoding('utf-8')
#     df = hd.get_all_stock_basics()
#     print df.dtypes
#     print df.head(2)
#     print df.index
#     print df.ix['000780']['timeToMarket']
#     print hd.get_frist_day('600848')
#     hd.get_all_history_tick(10)
#     tushare.get_index()

#     url = 'http://q.stock.sohu.com/hisHq?code=zs_000001&start=20150223&end=20160617&stat=1&order=D&period=d'
#     res = Request(url)
#     text = urlopen(res, timeout=10).read()
#     text = text.decode('GBK')
#     j = demjson.decode(text, 'utf-8')
#     head = ['date','open','close','change','pchange','low','heigh', 'vibration','volume','amount']#日期    开盘    收盘    涨跌额    涨跌幅    最低    最高    成交量(手)    成交金额(万)
#     data = []
#     for x in j[0].get('hq'):
#         m = tuple(x)
#         data.append([m[0], float(m[1]), float(m[2]), float(m[3]), '%.4f' % float(abs((float(m[2])-float(m[1])))/float(m[1])), float(m[5]), float(m[6]), '%.4f' %  float((float(m[1])-float(m[5]))/float(m[1])+ (float(m[6])-float(m[1]))/float(m[1])), float(m[7]), float(m[8]) ])
#     import pandas as pd
#     df = pd.DataFrame(data, columns=head)
#     print df.head()
#     df = df.drop(['empty'], axis=1)
#     df['code'] = 'zs_000001'
#     df.insert(1, 'code', 'sz000001')
#     df.insert(7,'amplitude', df['close']/df['open'])
#     df.to_csv('./test.csv', index=False, index_label='date')
#     print df.head(2)

#     hd.get_all_index(code, start, end)


from pyquery import PyQuery as pq
# from lxml import etree
import urllib
from bs4 import BeautifulSoup
# d = pq(url='http://data.10jqka.com.cn/market/dzjy/field/enddate/order/desc/page/1/ajax/1/')
page = urllib.urlopen('http://data.10jqka.com.cn/market/dzjy/field/enddate/order/desc/page/1/ajax/1/').read()
# BeautifulSoup在解析utf-8编码的网页时，如果不指定fromEncoding或者将fromEncoding指定为utf-8会出现中文乱码的现象。
# 解决此问题的方法是将Beautifulsoup构造函数中的fromEncoding参数的值指定为：gb18030
soup = BeautifulSoup(page, from_encoding="gb18030")
for tr in soup.select('tr'):
    print '###'
#     print tr
#     for td in tr.select('td'):
#         print '$$$$'
    if len(tr.select('td')) > 0:
        print tr.select('td')[8].get_text()
#         print type(tr.select('td')[1])
#     print type(tr.select('td'))
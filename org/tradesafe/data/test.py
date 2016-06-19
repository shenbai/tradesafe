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
    

    
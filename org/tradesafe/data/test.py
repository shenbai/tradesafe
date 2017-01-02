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
    # hd = HistoryData('/home/tack/stock')
    import sys

    try:
        url = 'http://q.stock.sohu.com/hisHq?code=cn_300197&start=20101010&end=20161231&stat=1&order=D&period=d'
        res = Request(url)
        text = urlopen(res, timeout=10).read()
        text = text.decode('GBK')

        j = demjson.decode(text, 'utf-8')
        head = ['date', 'open', 'close', 'chg', 'chg_r', 'low', 'heigh', 'vibration', 'volume',
                'amount', 'turnover']  # 日期    开盘    收盘    涨跌额    涨跌幅    最低    最高    成交量(手)    成交金额(万)
        # 日期	开盘	收盘	涨跌额	涨跌幅	最低	最高	成交量(手)	成交金额(万)	换手率
        data = []

        for x in j[0].get('hq'):
            print x
            date, open, close, change, _, low, heigh, valume, amount, turnover = x
            chg_r = '%.4f' % ((float(close) - float(open)) / float(open))
            vibration = '%.4f' % float((float(heigh) - float(low)) / float(open))
            chg_r = float(chg_r)
            vibration = float(vibration)
            data.append(
                [date, float(open), float(close), float(change), float(chg_r), float(low), float(heigh),
                 float(vibration), float(valume), float(amount), float(turnover[:-1])])

        # df = pd.DataFrame(data, columns=head)
        # if not df.empty:
        #     df.insert(1, 'code', code)
        #     sql_df = df.loc[:, :]
        #     sql.to_sql(sql_df, name='history_data', con=conn, index=False, if_exists='append')
        #     log.info('%s,%s,%d history data download ok.' % (code, str(start), len(sql_df)))
        #     break
    except Exception, e:
        print e
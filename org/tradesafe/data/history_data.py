# coding: utf-8
'''
Created on 2016年6月19日

@author: tack
'''
from datetime import datetime, date, timedelta
import os

from pandas.io import sql
from org.tradesafe.utils import utils
from org.tradesafe.data.index_code_conf import indices
from org.tradesafe.conf import config
from org.tradesafe.utils.memo import Memo
from org.tradesafe.db import sqlite_db as db
import pandas as pd
import tushare as ts
from urllib2 import Request, urlopen
import demjson


class HistoryData(object):
    '''
    历史数据获取
    '''

    def __init__(self, dataDir='.'):
        pass

    def get_all_stock_basics(self, useLocal=True):
        '''
        所有股票的基本数据
        useLocal:本地数据库的数据或者远程下载的数据
        return
        DataFrame
               code,代码
               name,名称
               industry,细分行业
               area,地区
               pe,市盈率
               outstanding,流通股本
               totals,总股本(万)
               totalAssets,总资产(万)
               liquidAssets,流动资产
               fixedAssets,固定资产
               reserved,公积金
               reservedPerShare,每股公积金
               eps,每股收益
               bvps,每股净资
               pb,市净率
               timeToMarket,上市日期
        '''
        conn = db.get_history_data_db()
        conn.text_factory = str
        df = None
        if useLocal:
            try:
                df = pd.read_sql_query('select * from stock_basics where [timeToMarket] !=0', conn)
                return df
            except Exception, e:
                print e
        df = ts.get_stock_basics()
        if not df.empty:
            try:
                sql_df=df.loc[:,:]
                sql.to_sql(sql_df, name='stock_basics', con=conn, index=True, if_exists='replace')
            except Exception, e:
                print e
        return df

    def get_all_stock_code(self):
        '''
        返回全部股票代码
        '''
        df = self.get_all_stock_basics();
        return df['code']

    def download_history_data_day(self, ktype='D'):
        '''
        获取近3年不复权的历史k线数据
        '''
        start = None
        conn = db.get_history_data_db(ktype)
        dic = {}
        try:
            row = conn.execute(config.sql_last_date_history_data).fetchone()
            start = row[0]
            dt = datetime.strptime(start, '%Y-%m-%d') + timedelta(days=1)
            start = datetime.strftime(dt, '%Y-%m-%d')
        except Exception, e:
            print e
        print start
        for code in self.get_all_stock_code():
            df = ts.get_hist_data(code=code, start=start, ktype=ktype)
            if df is not None:
                dic[code] = df
                df.insert(0, 'code', code)
                try:
                    sql_df=df.loc[:,:]
                    sql.to_sql(sql_df, name='history_data', con=conn, index=True, if_exists='append')
                except Exception, e:
                    print e
        return dic

    def get_history_data_day(self, ktype='D'):
        '''
        从sqlite中加载历史k线数据
        '''
        conn = db.get_history_data_db(ktype)
        try:
            df = pd.read_sql_query('select * from history_data', conn)
            return df
        except Exception, e:
            print e
        return None

    def get_all_day_hist_restoration(self):
        '''
        获取前复权的历史k线数据
        '''
        path = os.path.join(self.dataDir, 'history-day-restoration')
        utils.mkdirs(path)
        dic = {}
        for code in self.get_all_stock_code():
            df = ts.get_h_data(code, utils.today_last_year(3))
            if not df.empty:
                df.to_csv(os.path.join(path,code+'.csv'), index=True, encoding='utf-8')
                dic[code] = df
        return dic

    def get_all_history_tick(self, days=1):
        '''
        历史分笔数据
        '''
        path = os.path.join(self.dataDir, 'history-tick')
        utils.mkdirs(path)
        dic = {}
        for code in self.get_all_stock_code():
            alldf = pd.DataFrame()
            lasty = datetime.today().date() + timedelta(days=0-days)
            today = datetime.today().date()
            while today > lasty:
                if date.isoweekday(lasty) in[6,7]:
                    lasty = lasty + timedelta(+1)
                    continue
                df = ts.get_tick_data(code, lasty)
#                 df['date'] = str(lasty)
                df.insert(0, 'date', str(lasty))
                if len(df) < 10:
                    continue
                alldf = alldf.append(df[::])
                lasty = lasty + timedelta(+1)
            if not alldf.empty:
                alldf.to_csv(os.path.join(path,code+'.csv'), index=False, encoding='utf-8')
                dic[code] = alldf
        return alldf

    def download_all_index_history(self, start=None, end=None):
        '''
        start:开始时间 yyyyMMdd，第一次调用空则取一年前日期，之后以数据表中最近时间为准
        end:结束时间 yyyyMMdd，空则取当前日期
        '''
        conn = db.get_history_data_db()
        if start == None:
            try:
                onerow = conn.execute(config.sql_last_date_index_all).fetchone()
                if onerow != None:
                    start = onerow[0]
                    dt = datetime.strptime(start, '%Y-%m-%d') + timedelta(days=1)
                    start = datetime.strftime(dt, '%Y%m%d')
                else:
                    start = datetime.today().date() + timedelta(days=-365)
                    start = start.strftime('%Y%m%d')
            except Exception, e:
                start = datetime.today().date() + timedelta(days=-365)
                start = start.strftime('%Y%m%d')

        if end == None:
            end = datetime.today().date().strftime('%Y%m%d')
        print start, end
        if int(end)<= int(start):
            return None
        for code in indices.keys():
            url = 'http://q.stock.sohu.com/hisHq?code=%s&start=%s&end=%s&stat=1&order=D&period=d' % (code, start, end)
            res = Request(url)
            text = urlopen(res, timeout=10).read()
            text = text.decode('GBK')
            if len(text)< 40:
                continue
            j = demjson.decode(text, 'utf-8')
            head = ['date','open','close','change','pchange','low','heigh', 'vibration','volume','amount']#日期    开盘    收盘    涨跌额    涨跌幅    最低    最高    成交量(手)    成交金额(万)
            data = []
            for x in j[0].get('hq'):
                m = tuple(x)
                data.append([m[0], float(m[1]), float(m[2]), float(m[3]), '%.4f' % float(abs((float(m[2])-float(m[1])))/float(m[1])), float(m[5]), float(m[6]), '%.4f' %  float((float(m[1])-float(m[5]))/float(m[1])+ (float(m[6])-float(m[1]))/float(m[1])), float(m[7]), float(m[8]) ])
            df = pd.DataFrame(data, columns=head)
            if not df.empty:
                df.insert(1, 'code', code)
                try:
                    sql_df=df.loc[:,:]
                    sql.to_sql(sql_df, name='all_index', con=conn, index=False, if_exists='append')
                except Exception, e:
                    print e
        return df

    def get_all_index_history(self):
        con = db.get_history_data_db()
        df = pd.read_sql_query('select * from all_index order by date desc', con)
        return df

    def get_frist_day(self, code):
        '''
        上市日期
        '''
        df = self.get_all_stock_basics()
        return df.ix[code]['timeToMarket']

if __name__ == '__main__':
    hd = HistoryData('/home/tack/stock')
    hd.get_all_stock_basics()
    hd.download_all_index_history()
    df = hd.get_all_index_history()
    print df.head()
    # df = hd.get_all_stock_basics()
    # print len(df)
    # print len(df.loc[df.timeToMarket>0,:])
    # df = ts.get_stock_basics()
    # print df.head()
    hd.download_history_data_day(ktype='60')
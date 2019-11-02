# coding: utf-8
'''
Created on 2016年6月19日

@author: tack
'''
import os
import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
from org.tradesafe.conf import config
from org.tradesafe.db import sqlite_db as db
from org.tradesafe.utils import utils


class HistoryData(object):
    '''
    历史数据
    '''

    def __init__(self):
        self.log = utils.mylog
        self.history_data_db_conn = db.get_history_data_db()
        self.history_data_db_conn.text_factory = str

    def get_all_stock_basics(self):
        '''
        所有股票的基本数据
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
        
        try:
            df = pd.read_sql_query(
                'select * from stock_basics where [timeToMarket] !=0', self.history_data_db_conn)
            return df
        except Exception as e:
            self.log.info(e)
        return None

    def get_all_stock_code(self):
        '''
        返回全部股票代码
        '''
        df = self.get_all_stock_basics()
        return df['code'].values

    def get_history_data(self, ktype='D', code=None, startDate=None, endDate=None):
        '''
        从sqlite中加载历史k线数据
        '''

        # conn = db.get_history_data_db(ktype)

        try:
            # if code is not None and endDate is not None:
            #     df = pd.read_sql_query(config.sql_history_data_by_code_date_lt % (code,endDate), self.history_data_db_conn)
            # elif code is None and endDate is not None:
            #     df = pd.read_sql_query(config.sql_history_data_by_date_lt % endDate, self.history_data_db_conn)
            # elif code is not None and endDate is None:
            #     df = pd.read_sql_query(config.sql_history_data_by_code % code, self.history_data_db_conn)
            # elif code is None and endDate is None:
            #     df = pd.read_sql_query(config.sql_history_data_all, self.history_data_db_conn)

            if not startDate:
                startDate = '2010-01-01'
            if not endDate:
                endDate = datetime.now().strftime('%Y-%m-%d')

            df = pd.read_sql_query(config.sql_history_data_by_code_date_between % (
                code, startDate, endDate), self.history_data_db_conn)
            df = df.set_index(df['date'])
            return df
        except Exception as e:
            self.log.info(e)
        return None
    
    def get_history_data_one_day(self, ktype='D', code=None, kdate=None):
        '''
        从sqlite中加载历史k线数据
        '''

        # conn = db.get_history_data_db(ktype)
        try:
            if not kdate:
                kdate = datetime.now().strftime('%Y-%m-%d')
            df = pd.read_sql_query(config.sql_history_data_by_code_date % (
                code, kdate), self.history_data_db_conn)
            df = df.set_index(df['date'])
            return df
        except Exception as e:
            self.log.info(e)
        return None

    def get_history_data_all(self, ktype='D', startDate=None, endDate=None):
        # conn = db.get_history_data_db(ktype)
        try:
            if not startDate:
                startDate = '2010-01-01'
            if not endDate:
                endDate = datetime.now().strftime('%Y-%m-%d')
            df = pd.read_sql_query(config.sql_history_data_by_date_between % (startDate, endDate), self.history_data_db_conn)
            # df = df.set_index(df['date'])
            return df
        except Exception as e:
            self.log.error(e)
        return None

    def get_history_data_qfq(self, code=None, startDate=None, endDate=None):
        '''
        获取前复权的历史k线数据
        '''

        # conn = db.get_history_data_db()
        try:
            df = pd.read_sql_query(config.sql_history_data_qfq_by_code_date_between % (
                code, startDate, endDate), self.history_data_db_conn)
            return df
        except Exception as e:
            self.log.error(e)
        return None

    def get_index_history(self, code=None):
        # con = db.get_history_data_db()
        if code is None:
            df = pd.read_sql_query(
                'select * from all_index order by code, date([date]) asc', self.history_data_db_conn)
        else:
            df = pd.read_sql_query(
                'select * from all_index where code="%s" order by date([date]) asc' % code, self.history_data_db_conn)
        df = df.set_index(df['date'])
        return df

    def get_frist_day(self, code):
        '''
        上市日期
        '''
        df = self.get_all_stock_basics()
        return df.ix[code]['timeToMarket']


if __name__ == '__main__':
    hd = HistoryData()
    hd.get_all_stock_basics()
    # hd.get_index_history()
    df = hd.get_history_data(
        code='600622', startDate='2015-01-01', endDate='2016-06-01')
    print(df.head())

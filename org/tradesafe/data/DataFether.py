# coding:utf-8

from datetime import datetime, time, timedelta
import os

from pandas.io import sql
from org.tradesafe.utils import utils
from org.tradesafe.data.index_code_conf import indices
from org.tradesafe.conf import config
from org.tradesafe.db import sqlite_db as db
import pandas as pd
import tushare as ts
from urllib2 import Request, urlopen
import demjson
from org.tradesafe.conf import config
from org.tradesafe.utils import utils
utils.mkdirs(config.log_dir)
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='%s/historydown.log' % config.log_dir)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# 设置日志打印格式
formatter = logging.Formatter(
    '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
# 将定义好的console日志handler添加到root logger
logging.getLogger('').addHandler(console)


def get_all_stock_code():
    '''
    返回全部股票代码
    '''
    conn = db.get_history_data_db()
    conn.text_factory = str
    try:
        df = pd.read_sql_query(
            'select * from stock_basics where [timeToMarket] !=0', conn)
        return df['code']
    except Exception, e:
        print e


def updata_all_stock_basics():
    '''
    更新所有股票的基本数据
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
    df = ts.get_stock_basics()
    if not df.empty:
        try:
            sql_df = df.loc[:, :]
            sql.to_sql(sql_df, name='stock_basics', con=conn,
                       index=True, if_exists='replace')
        except Exception, e:
            print e


def download_history_data(ktype='D', startTime=None):
    '''
    获取近3年不复权的历史k线数据
    '''
    start = startTime
    conn = db.get_history_data_db(ktype)
    cost = 0

    for code in get_all_stock_code():
        cost = datetime.now()
        df = ts.get_hist_data(code=code, start=start, ktype=ktype)
        if df is not None and len(df) > 0:
            df.insert(0, 'code', code)
            try:
                sql_df = df.loc[:, :]
                sql.to_sql(sql_df, name='history_data', con=conn,
                           index=True, if_exists='append')
                logging.info('%s,%s,%d history data download ok.' % (code, str(start), len(sql_df)))
            except Exception, e:
                logging.error('error:code:%s,start:%s' % (code, start))
                print e
        else:
            logging.info('%s,%s get none' % (code, start))
        logging.debug('%s,costs:%d s' %
                      (code, (datetime.now() - cost).seconds))

def download_history_data_fq(autype='qfq', startTime=None):
    '''
    获取前复权的历史k线数据
    '''

    conn = db.get_history_data_db('D')
    start = startTime
    if startTime is None:
        start = utils.today_last_year(6)

    for code in get_all_stock_code():
        df = ts.get_h_data(code, start=start, drop_factor=False)
        if df is not None:
            try:
                df.insert(0, 'code', code)
                sql_df = df.loc[:, :]
                sql.to_sql(sql_df, name='history_data_%s' %
                           autype, con=conn, index=True, if_exists='append')
                logging.info('%s,%s history qfq data download ok.' %
                             (code, start))
            except Exception, e:
                logging.error('error:code:%s,start:%s' % (code, start))
                print e


def download_index_history_data(start=None, end=None):
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
                start = datetime.today().date() + timedelta(days=-365 * 3)
                start = start.strftime('%Y%m%d')
        except Exception, e:
            start = datetime.today().date() + timedelta(days=-365 * 3)
            start = start.strftime('%Y%m%d')

    if end == None:
        end = datetime.today().date().strftime('%Y%m%d')
    print start, end
    if int(end) <= int(start):
        return None
    for code in indices.keys():
        url = 'http://q.stock.sohu.com/hisHq?code=%s&start=%s&end=%s&stat=1&order=D&period=d' % (
            code, start, end)
        res = Request(url)
        text = urlopen(res, timeout=10).read()
        text = text.decode('GBK')
        if len(text) < 40:
            continue
        j = demjson.decode(text, 'utf-8')
        head = ['date', 'open', 'close', 'change', 'pchange', 'low', 'heigh', 'vibration', 'volume',
                'amount']  # 日期    开盘    收盘    涨跌额    涨跌幅    最低    最高    成交量(手)    成交金额(万)
        data = []
        for x in j[0].get('hq'):
            m = tuple(x)
            data.append([m[0], float(m[1]), float(m[2]), float(m[3]),
                         '%.4f' % float(
                             abs((float(m[2]) - float(m[1]))) / float(m[1])), float(m[5]), float(m[6]),
                         '%.4f' % float(
                             (float(m[1]) - float(m[5])) / float(m[1]) + (float(m[6]) - float(m[1])) / float(m[1])),
                         float(m[7]), float(m[8])])
        df = pd.DataFrame(data, columns=head)
        if not df.empty:
            df.insert(1, 'code', code)
            try:
                sql_df = df.loc[:, :]
                sql.to_sql(sql_df, name='all_index', con=conn,
                           index=False, if_exists='append')
                logging.info('%s,%s index history download ok.' %
                             (code, start))
            except Exception, e:
                print e
    return df


def download_dd_data(start=None):
    '''
    获取大单数据
    '''
    conn = db.get_dd_data_db()
    start = start
    if start is None:
        start = utils.today_last_year(1)
    for code in get_all_stock_code():

        end = datetime.today().date()
        while start < end:
            date = end.strftime('%Y-%m-%d')
            df = ts.get_sina_dd(code=code, date=date, vol=500)
            if df is not None:
                df.insert(0, 'code', code)
                try:
                    sql_df = df.loc[:, :]
                    sql.to_sql(sql_df, name='dd_data', con=conn,
                               index=True, if_exists='append')
                    logging.info('%s,%s dd data download ok.' % (code, start))
                except Exception, e:
                    logging.error('download error:%s,%s' % (code, date))
                    print e
                pass
            start = start + timedelta(days=1)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--update_basics', help='update all stock basics', action='store_true')
    parser.add_argument('-d', dest='start', help='download history data', action='store')
    parser.add_argument('-dqfq', '--download_qfq', help='download history data (qfq)', action='store_true')
    parser.add_argument('-di', '--download_index', help='download index data', action='store_true')
    parser.add_argument('-dd', '--download_dd', help='download dd data', action='store_true')
    args = parser.parse_args()
    print args.start
    if args.update_basics:
        # download basics
        updata_all_stock_basics()
    if args.start:
        if 'None' == args.start:
            download_history_data(startTime=None)
        else:
            download_history_data(startTime=args.start)
    if args.download_qfq:
        download_history_data_fq()
    if args.download_index:
        download_index_history_data(start='20140101')
    if args.download_dd:
        download_dd_data()

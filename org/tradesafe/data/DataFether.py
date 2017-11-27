# coding:utf-8

from datetime import datetime, timedelta
# from urllib import Request, urlopen
from urllib import request

import demjson
import pandas as pd
import tushare as ts
from pandas.io import sql

from org.tradesafe.bt.log import logging as log
from org.tradesafe.conf import config
from org.tradesafe.data.index_code_conf import indices
from org.tradesafe.db import sqlite_db as db
from org.tradesafe.utils import utils

utils.mkdirs(config.log_dir)
log = utils.mylog
slog = utils.statelog
get_laste_update_dt = utils.get_laste_update_dt

retry = 3
# 历史数据
sohu_history_api = 'http://q.stock.sohu.com/hisHq?code=%s&start=%s&end=%s&stat=1&order=D&period=d'
sina_money_flow_api = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_qsfx_zjlrqs?page=1&num=%d&sort=opendate&asc=0&daima=%s'
default_start_time = '20100101'


def append_stock_perfix(code):
    if code.startswith('00') or code.startswith('30'):
        return 'sz%s' % code
    if code.startswith('60'):
        return 'sh%s' % code


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
    except Exception as e:
        log.error(e)


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
    retry = 3
    for i in range(retry):
        try:
            df = ts.get_stock_basics()
            if not df.empty:
                sql_df = df.loc[:, :]
                sql.to_sql(sql_df, name='stock_basics', con=conn,
                           index=True, if_exists='replace')
                log.info('all stock basics updated, total size=%d' % len(df))
                break
        except Exception as e:
            log.error(e)
    conn.close()


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
                log.info('%s,%s history qfq data download ok.' % (code, start))
            except Exception as e:
                log.error('error:code:%s,start:%s' % (code, start))


def download_history_data(ktype='D', start=None, end=None, init_run=False):
    '''
    获取近不复权的历史k线数据
    '''
    if init_run:
        start = default_start_time
    if end == None:
        end = datetime.today().date().strftime('%Y%m%d')

    conn = db.get_history_data_db(ktype)
    cost = 0
    cur_time = datetime.now()

    for code in get_all_stock_code():
        cost = datetime.now()
        if start is None:
            _start = get_laste_update_dt(code)
            if _start is not None:
                dt = datetime.strptime(_start, '%Y-%m-%d') + timedelta(days=1)
                start = datetime.strftime(dt, '%Y%m%d')
            else:
                row = conn.execute(config.sql_last_date_history_data_by_code % code).fetchone()
                if row is not None:
                    start = row[0]
                    dt = datetime.strptime(start, '%Y-%m-%d') + timedelta(days=1)
                    start = datetime.strftime(dt, '%Y%m%d')
                else:
                    start = default_start_time
        for i in range(retry):
            try:
                url = sohu_history_api % ('cn_' + code, start, end)
                text = request.urlopen(url, timeout=10).read()
                text = text.decode('GBK')
                log.info('url=%s,size=%d, try=%d' % (url, len(text), i))
                if len(text) < 20:
                    continue
                j = demjson.decode(text, 'utf-8')
                head = ['date', 'open', 'close', 'chg', 'chg_r', 'low', 'high', 'vibration', 'volume',
                        'amount', 'turnover']  # 日期    开盘    收盘    涨跌额    涨跌幅    最低    最高    成交量(手)    成交金额(万)
                # 日期	开盘	收盘	涨跌额	涨跌幅	最低	最高	成交量(手)	成交金额(万)	换手率
                data = []

                for x in j[0].get('hq'):
                    date, open, close, change, _, low, high, valume, amount, turnover = x
                    if '-' == turnover:
                        turnover = '0.0%'
                    chg_r = '%.4f' % ((float(close) - float(open)) / float(open))
                    vibration = '%.4f' % float((float(high) - float(low)) / float(open))
                    chg_r = float(chg_r)
                    vibration = float(vibration)
                    data.append(
                        [date, float(open), float(close), float(change), float(chg_r), float(low), float(high),
                         float(vibration), float(valume), float(amount), float(turnover[:-1])])

                df = pd.DataFrame(data, columns=head)
                if not df.empty:
                    df.insert(1, 'code', code)
                    sql_df = df.loc[:, :]
                    sql.to_sql(sql_df, name='history_data', con=conn, index=False, if_exists='append')
                    log.info('%s,%s,%d history data download ok.' % (code, str(start), len(sql_df)))
                    slog.info('%s,%s' % (code, data[0][0]))
                    break
            except Exception as e:
                log.error('error:code=%s,start=%s,msg=%s' % (code, start, e))
                if str(e).find('UNIQUE constraint') > -1:
                    break
        log.debug('%s,costs:%d s' % (code, (datetime.now() - cost).seconds))
    conn.close()
    log.info('history data download complete. cost %d s' % (datetime.now() - cur_time).seconds)


def download_index_history_data(start=None, end=None, init_run=False):
    '''
    start:开始时间 yyyyMMdd，第一次调用空则取20100101，之后以数据表中最近时间为准
    end:结束时间 yyyyMMdd，空则取当前日期
    '''
    cur_time = datetime.now()
    conn = db.get_history_data_db()
    if init_run:
        start = default_start_time
    if start is None:
        try:
            onerow = conn.execute(config.sql_last_date_index_all).fetchone()
            if onerow is not None:
                start = onerow[0]
                dt = datetime.strptime(start, '%Y-%m-%d') + timedelta(days=1)
                start = datetime.strftime(dt, '%Y%m%d')
            else:
                start = default_start_time
        except Exception as e:
            start = default_start_time

    if end is None:
        end = datetime.today().date().strftime('%Y%m%d')
    print(start, end)
    if int(end) <= int(start):
        return None
    for code in indices.keys():
        for i in range(retry):
            try:
                url = sohu_history_api % (code, start, end)

                text = request.urlopen(url, timeout=10).read()
                text = text.decode('GBK')
                log.info('url=%s,size=%d, try=%d' % (url, len(text), i))
                if len(text) < 20:
                    continue
                j = demjson.decode(text, 'utf-8')
                head = ['date', 'open', 'close', 'chg', 'chg_r', 'low', 'high', 'vibration', 'volume',
                        'amount']  # 日期    开盘    收盘    涨跌额    涨跌幅    最低    最高    成交量(手)    成交金额(万)
                # 日期	开盘	收盘	涨跌额	涨跌幅	最低	最高	成交量(手)	成交金额(万)	换手率
                data = []
                for x in j[0].get('hq'):
                    date, open, close, change, _, low, high, valume, amount, _ = x
                    chg_r = '%.4f' % ((float(close) - float(open)) / float(open))
                    vibration = '%.4f' % (float((float(high) - float(low)) / float(open)))
                    # print date, vibration, str(float(vibration))
                    data.append([date, float(open), float(close), float(change), float(chg_r), float(low), float(high),
                                 float(vibration), float(valume), float(amount)])

                    # sql_str = 'insert OR IGNORE into all_index values(?,?,?,?,?,?,?,?,?,?,?)'
                    # print len(data[0])
                    # conn.executemany(sql_str, data)
                df = pd.DataFrame(data, columns=head)
                if not df.empty:
                    df.insert(1, 'code', code)
                    sql_df = df.loc[:, :]
                    sql.to_sql(sql_df, name='all_index', con=conn, index=False, if_exists='append')
                    log.info('%s,%s index history download ok.' % (code, start))
                    break
            except Exception as e:
                log.error(e)
    conn.close()
    log.info('index history data download complete. cost %d s' % (datetime.now() - cur_time).seconds)


def download_money_flow_data(num=1000):
    '''
    get money flow from sina finance
    :param num:
    :return:
    '''
    conn = db.get_money_flow_db()
    cur_time = datetime.now()
    for code in get_all_stock_code():
        code = append_stock_perfix(code)
        cost = datetime.now()
        for i in range(retry):
            try:
                url = sina_money_flow_api % (num, code)
                text = request.urlopen(url, timeout=10).read()
                text = text.decode('GBK')
                log.info('url=%s,size=%d, try=%d' % (url, len(text), i))
                if len(text) < 10:
                    continue
                # j = demjson.decode(text, 'utf-8') #json很大的时候效率非常查
                text = text[2:-2]
                j = text.replace('"', '').split('},{')
                head = ['date', 'close', 'chg_r', 'turnover', 'netamount', 'ratio', 'zl_netamount', 'zl_ratio',
                        'cat_ratio']
                # 日期	收盘价	涨跌幅	换手率	净流入   	净流入率	主力净流入	    主力净流入率	行业净流入率
                data = []

                for x in j:
                    m = {}
                    for s in x.split(','):
                        k, v = s.split(':')
                        if '-' == v or 'null' == v:
                            v = '0.0'
                        m[k] = v
                    date = m['opendate']
                    close = float(m['trade'])
                    chg_r = float(m['changeratio'])
                    turnover = float(m['turnover']) / 10000
                    netamount = float(m['netamount']) / 10000
                    ratio = float(m['ratioamount'])
                    zl_netamount = float(m['r0_net']) / 10000
                    zl_ratio = float(m['r0_ratio'])
                    cat_ratio = float(m['cate_ra'])
                    data.append([date, close, chg_r, turnover, netamount, ratio, zl_netamount, zl_ratio, cat_ratio])

                df = pd.DataFrame(data, columns=head)
                log.info('data ok')
                if not df.empty:
                    df.insert(1, 'code', code)
                    sql_df = df.loc[:, :]
                    sql.to_sql(sql_df, name='money_flow', con=conn, index=False, if_exists='append')
                    log.info('%s,%s,%d money flow data download ok.' % (code, str(start), len(sql_df)))
                    break
            except Exception as e:
                log.error('error:code=%s,start=%s,msg=%s' % (code, start, e))
        log.debug('%s,costs:%d s' % (code, (datetime.now() - cost).seconds))
    conn.close()
    log.info('money flow data download complete. cost %d s' % (datetime.now() - cur_time).seconds)

    pass


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
                    log.info('%s,%s dd data download ok.' % (code, start))
                except Exception as e:
                    log.error('download error:%s,%s' % (code, date))
                pass
            start = start + timedelta(days=1)


if __name__ == '__main__':
    # download_index_history_data(init_run=True)
    #
    # import sys
    # sys.exit(0)
    # exit(0)

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--update_basics', help='update all stock basics', action='store_true')
    parser.add_argument('-d', '--download', help='download history data', action='store_true')
    parser.add_argument('-dqfq', '--download_qfq', help='download history data (qfq)', action='store_true')
    parser.add_argument('-di', '--download_index', help='download index data', action='store_true')
    parser.add_argument('-dd', '--download_dd', help='download dd data', action='store_true')
    parser.add_argument('-dmf', '--download_money_flow', help='down load money flow data', action='store_true')
    parser.add_argument('--start', help='start time', action='store')
    parser.add_argument('--end', help='end time', action='store')
    parser.add_argument('--num', help='number of items per page', action='store')
    parser.add_argument('--init_run', help='init_run or not', action='store')

    args = parser.parse_args()

    start, end, num = None, None, None
    if args.start is not None:
        start = args.start
    if args.end is not None:
        end = args.end
    if args.num is not None:
        num = args.num

    if args.update_basics:
        # download basics
        updata_all_stock_basics()

    if args.download:
        if args.init_run:
            download_history_data(start=start, end=end, init_run=True)
        else:
            download_history_data(start=start, end=end)

    if args.download_qfq:
        download_history_data_fq()

    if args.download_index:
        if args.init_run:
            download_index_history_data(start=start, end=end, init_run=True)
        else:
            download_index_history_data(start=start, end=end)

    if args.download_dd:
        download_dd_data()

    if args.download_money_flow:
        if args.num is not None:
            download_money_flow_data(int(args.num))
        else:
            download_money_flow_data()

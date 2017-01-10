# coding:utf-8

from org.tradesafe.data.history_data import HistoryData
from org.tradesafe.bt.account import Account
from org.tradesafe.bt.strategy import AbstrictStrategy
from org.tradesafe.bt import strategy
from org.tradesafe.bt.order import Order
from org.tradesafe.bt.btdata import BtData
from org.tradesafe.bt.log import logging as logger
from datetime import datetime, timedelta
import traceback
import sys
from math import *
import talib


class StrategyCci(AbstrictStrategy):
    '''
    strategy
    '''

    def handle_tick(self, tick, data, row):
        '''
        Args:
            tick: 当天日期yyyy-mm-dd
            data: 从开始日期到当前日期的全部数据
            row: 当前日期（当日）数据
        Returns:
        '''
        yestoday = self.get_one_data(data, -1)
        if row.cci < -100:
            if not self.acount.buy_restriction_filter(data):
                self.acount.buy(row.code, row.close, num=100000, date=tick)
                if self.begin is None:
                    self.begin = tick
        elif row.code in self.acount.positions and row.cci > 100:
            if not self.acount.sell_restriction_filter(data):
                self.acount.sell(row.code, row.close, num=100000, date=tick)
        pass


if __name__ == '__main__':

    # code = '600366'
    start = '2016-01-01'
    end = '2016-08-01'
    X = []
    hd = HistoryData()
    # codes = hd.get_all_stock_code()
    # data = hd.get_history_data_all(startDate=start, endDate=end)
    # strategy.bench_mark(codes, data, start=start, end=end)
    # sys.exit(0)
    start = '2016-01-01'
    end = '2016-08-01'
    X = []
    hd = HistoryData()
    codes = hd.get_all_stock_code()
    codes = ['600180', '000002']

    a = StrategyCci(stock_pool=codes, start=start, end=end)
    a.run()
    import matplotlib.pyplot as plt
    import pandas as pd
    import matplotlib
    matplotlib.style.use('ggplot')

    # print a.acount.cash, a.acount.get_market_value(), a.acount.get_assets(), a.acount.get_position_profit()


    # for ph in a.acount.history_positions.get_history(code):
    #     print ph
    # print '############################# history order #####################'


    t_times = 0
    for code in codes:
        t = pd.DataFrame(index=a.btData.datas[code].index)
        # print a.btData.datas[code].head()
        # t['c'] = a.btData.datas[code].close
        # t['ma5'] = a.btData.datas[code].ma5
        # t['ma10'] = a.btData.datas[code].ma10
        # t['beta'] = a.btData.datas[code].beta
        # t['l_angle'] = a.btData.datas[code].l_angle
        # t['l_intercept'] = a.btData.datas[code].l_intercept
        # t['l_slope'] = a.btData.datas[code].l_slope
        # t['sar'] = a.btData.datas[code].sar
        bs = []
        t['bs'] = 0
        # print t['sar']
        # print t.tail()
        # plt.figure()
        if a.acount.history_orders.get_history(code):
            print len(a.acount.history_orders.get_history(code)), 'trade'
            t_times = len(a.acount.history_orders.get_history(code))
            for oh in a.acount.history_orders.get_history(code):
                logger.info('order#%s' % oh)
                if oh.date in t.index:
                    if 'buy' == oh.cmd:
                        # t.ix[oh.date]['bs'] = 5
                        t['bs'][oh.date] = 1
                    elif 'sell' == oh.cmd:
                        t['bs'][oh.date] = -1
                    # t.ix[oh.date]['bs']= oh.cmd

            # t.ix['2015-08-07']['bs'] = 10
            # print t.ix['2015-08-07']['bs']
            # print '############################# history assets #####################'
            # for x in a.acount.history_assets:
            #     print x
            # print 'total_profit=', a.acount.history_orders.get_total_profit(code)
            # print a.acount.cash, a.acount.get_market_value(), a.acount.get_assets(), a.acount.get_position_profit()

            logger.info( '~ '+ code +'\t'+ str(a.baseline(sync=False)) +'\t'+ str((a.acount.get_assets() - a.acount.initial_cash)/a.acount.initial_cash))
            # print t.describe()
            # t.plot()
            # plt.show()
    X.append((a.baseline(sync=False), (a.acount.get_assets() - a.acount.initial_cash)/a.acount.initial_cash))
    print X
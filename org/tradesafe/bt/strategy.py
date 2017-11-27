# coding:utf-8

from org.tradesafe.data.history_data import HistoryData
from org.tradesafe.bt.account import Account
from org.tradesafe.bt.order import Order
from org.tradesafe.bt.btdata import BtData
from org.tradesafe.bt.log import logging as logger
from datetime import datetime, timedelta
import traceback
import sys
from math import *
import talib


class abstrictStrategy(object):
    '''
    strategy
    '''

    def __init__(self, stock_pool=['000001'], **kwargs):
        self.hd = HistoryData()
        self.stock_pool = stock_pool
        start_date = kwargs.get('start')
        end_date = kwargs.get('end')
        if start_date is None or end_date is None:
            raise Exception('no start,end time set')
        logger.info('load data...')
        self.btData = BtData(stock_pool=stock_pool, **kwargs)
        self.btData.indicator()
        logger.info('load data completed')
        self.curr_tick = 0
        self.curr_tick_pos = 0
        self.begin = None
        self.end = None
        if 'acount' in kwargs:
            self.acount = kwargs.get('acount')
        else:
            self.acount = Account(max_position=1., min_position=0., max_position_per_stock=1.)

    def run(self):
        '''
        strategy goes here
        Returns:
        '''
        # dataFrames = self.datas.values()
        for tick in self.btData.ticks:
            try:
                for df in self.btData.datas.values():
                    row = df.ix[tick]
                    self.curr_tick = tick
                    self.curr_tick_pos += 1
                    if len(row) > 3:
                        # self.acount.update_price_of_position(code=row.code, price=row.close, date=tick)
                        order = self.handle_tick(tick=tick, data=df.ix[:tick], row=row)
                        self.acount.update_price_of_position(code=row.code, price=row.close, date=tick)
                        if self.begin is None:
                            self.begin = tick
                        self.end = tick
            except Exception as e:
                logger.info('error %s' % e)
                if not isinstance(e, KeyError):
                    pass
                # traceback.print_exc()
                # ignore
                pass


    def baseline(self):
        '''
        等权买入并持有
        '''
        b = 0.
        e = 0.
        for data in self.btData.datas.values():
            b += data.ix[self.begin].close
            e += data.ix[self.end].close
            print self.begin, data.ix[self.begin].close
            print self.end, data.ix[self.end].close
        n = len(self.btData.datas)
        print b/n, e/n
        return (e/n - b/n) / b/n

    def handle_tick(self, tick, data, row):
        '''
        Args:
            tick: 当天日期yyyy-mm-dd
            data: 从开始日期到当前日期的全部数据
            row: 当前日期（当日）数据
        Returns:
        '''
        yestoday = self.get_one_data(data, -1)
        if row.close < row.lowerband * 1.1:
            # print 'buy', row.close, row.middleband, row.date
            self.acount.buy(row.code, row.close, num=1000, date=tick)

        if row.close > row.middleband and row.middleband > row.lowerband*1.1:
            # print 'sell:' ,  row.close, row.middleband, row.date
            self.acount.sell(row.code, row.close, num=1000, date=tick)
        pass

    def get_one_data(self, data, i):
        if i < 0:
            if i < 0 and self.curr_tick_pos + i >= 0:
                return data.ix[self.btData.ticks[self.curr_tick_pos + i]]
        return None

class Metrics(object):
    """docstring for Metrics"""

    def __init__(self, **kwargs):
        self.hd = kwargs.get('hd', HistoryData())
        self.ticks = kwargs.get('ticks')
        if 'index_code' in kwargs:
            self.index_code = kwargs.get('index_code')
        else:
            self.index_code = 'zs_000001'

        self.index_data = self.hd.get_index_history(self.index_code)
        # print self.index_data.tail()
        pass

    def baseline(self):
        b = 0.
        e = 0.
        try:
            # b = self.index_data.ix[begin]
            b = self.index_data.ix[self.index_data.index[0]].close
        except Exception, e:
            pass
        try:
            # e = self.index_data.ix[end]
            e = self.index_data.ix[self.index_data.index[-1]].close
        except Exception, e:
            pass
        print b, e
        return (e - b) / b

if __name__ == '__main__':

    a = abstrictStrategy(stock_pool=['600036'], start='2015-01-01', end='2016-12-01')
    import pandas as pd
    import numpy as np
    import matplotlib.colors as colors
    import matplotlib.finance as finance
    import matplotlib.dates as mdates
    import matplotlib.ticker as mticker
    import matplotlib.mlab as mlab
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as font_manager

    t = pd.DataFrame(index=a.btData.datas['600036'].index)
    t['c'] = a.btData.datas['600036'].close
    # t['sar'] = a.btData.datas['600036'].sar
    # print t.tail()

    t['bu'] = a.btData.datas['600036'].upperband
    t['mi'] = a.btData.datas['600036'].middleband
    t['lo'] = a.btData.datas['600036'].lowerband

    # plt.figure()
    t.plot()
    plt.show()

    # print a.acount.cash, a.acount.get_market_value(), a.acount.get_assets(), a.acount.get_position_profit()
    # a.run()

    # for ph in a.acount.history_positions.get_history('600036'):
    #     print ph
    # print '############################# history order #####################'
    # for oh in a.acount.history_orders.get_history('600036'):
    #     print oh
    # print '############################# history assets #####################'
    # for x in a.acount.history_assets:
    #     print x
    # print 'total_profit=', a.acount.history_orders.get_total_profit('600036')
    #
    # print a.acount.cash, a.acount.get_market_value(), a.acount.get_assets(), a.acount.get_position_profit()
    #
    #
    # print a.baseline(), (a.acount.get_assets() - a.acount.initial_cash)/a.acount.initial_cash
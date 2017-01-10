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


class AbstrictStrategy(object):
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
                self.curr_tick = tick
                self.curr_tick_pos += 1
                for df in self.btData.datas.values():
                    row = df.ix[tick]
                    if len(row) > 3 and tick in df.index:
                        order = self.handle_tick(tick=tick, data=df.ix[:tick], row=row)
                        self.acount.update_price_of_position(code=row.code, price=row.close, date=tick)
                        # if self.begin is None:
                        #     self.begin = tick
                        self.end = tick
            except Exception as e:

                if isinstance(e, KeyError):
                    pass
                else:
                    logger.info('error %s' % e)
                    traceback.print_exc()
                # ignore
                pass


    def baseline(self, sync=False):
        '''
        等权买入并持有
        '''
        b = 0.
        e = 0.
        for data in self.btData.datas.values():
            if sync:
                b += data.ix[self.begin].close
                e += data.ix[self.end].close
                logger.info('#SYNC\t%s=>%f,%s=>%f' % (self.begin, data.ix[self.begin].close, self.end, data.ix[self.end].close))
            else:
                b += data.ix[0].close
                e += data.ix[-1].close
                logger.info('#!SYNC\t%s=>%f,%s=>%f' % (data.ix[0].date, data.ix[0].close, data.ix[-1].date, data.ix[-1].close))
        n = len(self.btData.datas)
        logger.info('avg_b=%f, avg_e=%f' % (b/n, e/n))
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
        # if row.close < row.lowerband :
        # if row.beta < 0.1:#good
        if row.beta < 0.05:
        # if row.l_slope > 0 and row.beta < 0.1:
            # print 'buy', row.close, row.middleband, row.date
            if not self.acount.buy_restriction_filter(data):
                self.acount.buy(row.code, row.close, num=100000, date=tick)
                if self.begin is None:
                    self.begin = tick

        # if row.close > row.middleband and row.middleband > row.lowerband*1.1:
        #     # print 'sell:' ,  row.close, row.middleband, row.date
        #     self.acount.sell(row.code, row.close, num=1000000, date=tick)
        # print row.lowerband, row.middleband,row.upperband, row.close
        elif row.code in self.acount.positions and row.beta > 2:
                        # row.close > row.sar:
                        #self.acount.positions[row.code].get_profit_ratio() > 10:
            if not self.acount.sell_restriction_filter(data):
                self.acount.sell(row.code, row.close, num=100000, date=tick)
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

def bench_mark(codes, all_data, strategy=None, **kwargs):
    import matplotlib.pyplot as plt
    import pandas as pd
    import matplotlib
    matplotlib.style.use('ggplot')
    start = kwargs.get('start', '2016-01-01')
    end = kwargs.get('end', '2016-08-01')
    for code in codes:
        try:
            a = AbstrictStrategy(stock_pool=[code], start=start, end=end, data=all_data)
            t = pd.DataFrame(index=a.btData.datas[code].index)
            # print a.btData.datas[code].head()
            # t['c'] = a.btData.datas[code].close
            # t['ma5'] = a.btData.datas[code].ma5
            # t['ma10'] = a.btData.datas[code].ma10
            t['beta'] = a.btData.datas[code].beta
            bs = []
            a.run()
            t['bs'] = 0
            t_times = 0
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

                logger.info( '~ '+ code +'\t'+ str(a.baseline()) +'\t'+ str((a.acount.get_assets() - a.acount.initial_cash)/a.acount.initial_cash))
                X.append((code, a.baseline(), (a.acount.get_assets() - a.acount.initial_cash)/a.acount.initial_cash))
                # print t.describe()
                # t.plot()
                # plt.show()
        except Exception, e:
            traceback.print_exc()
            pass
    print X

if __name__ == '__main__':

    code = '600246'
    start = '2016-01-01'
    end = '2016-08-01'
    X = []
    hd = HistoryData()
    codes = hd.get_all_stock_code()
    data = hd.get_history_data_all(startDate=start, endDate=end)
    bench_mark(codes, data, start=start, end=end)
    sys.exit(0)

    for code in codes:
        a = AbstrictStrategy(stock_pool=[code], start=start, end=end)
        import matplotlib.pyplot as plt
        import pandas as pd
        import matplotlib
        matplotlib.style.use('ggplot')
        t = pd.DataFrame(index=a.btData.datas[code].index)
        # print a.btData.datas[code].head()
        # t['c'] = a.btData.datas[code].close
        # t['ma5'] = a.btData.datas[code].ma5
        # t['ma10'] = a.btData.datas[code].ma10
        t['beta'] = a.btData.datas[code].beta
        # t['l_angle'] = a.btData.datas[code].l_angle
        # t['l_intercept'] = a.btData.datas[code].l_intercept
        # t['l_slope'] = a.btData.datas[code].l_slope
        # t['sar'] = a.btData.datas[code].sar
        # print t['sar']
        # print t.tail()
        # plt.figure()
        # print a.acount.cash, a.acount.get_market_value(), a.acount.get_assets(), a.acount.get_position_profit()
        a.run()

        # for ph in a.acount.history_positions.get_history(code):
        #     print ph
        # print '############################# history order #####################'

        bs = []
        t['bs'] = 0
        t_times = 0
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

            logger.info( '~ '+ code +'\t'+ str(a.baseline()) +'\t'+ str((a.acount.get_assets() - a.acount.initial_cash)/a.acount.initial_cash))
            X.append((code, a.baseline(), (a.acount.get_assets() - a.acount.initial_cash)/a.acount.initial_cash))
            # print t.describe()
            # t.plot()
            # plt.show()
    print X
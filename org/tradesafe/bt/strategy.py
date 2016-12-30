# coding:utf-8

from org.tradesafe.data.history_data import HistoryData
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
        self.datas = {}
        for stock in self.stock_pool:
            self.datas[stock] = self.hd.get_history_data(
                code=stock, startDate=start_date, endDate=end_date)
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        self.ticks = []
        while start <= end:
            if start.weekday() < 5:
                self.ticks.append(start.strftime('%Y-%m-%d'))
            start = start + timedelta(days=1)
        if 'acount' in kwargs:
            self.acount = kwargs.get('acount')
        else:
            self.acount = Acount(maxPosition=1, maxPositionPerShare=0.2)
        if 'metrics' in kwargs:
            self.metrics = kwargs.get('metrics')
        else:
            self.metrics = Metrics(
                index_code='zs_000001', ticks=self.ticks, hd=self.hd)
        self.order = Order(self.acount)
        self.begin = None
        self.end = None
        self.p = 0

        self.indicator()


    def indicator(self, **kwargs):
        print '#####'
        for df in self.datas.values():
            macd, macdsignal, macdhist = talib.MACD(df.close.values, fastperiod=12, slowperiod=26, signalperiod=9)
            df['macd'] = macd
            df['macdsignal'] = macdsignal
            df['macdhist'] = macdhist
            k, d = talib.STOCH(df.high.values, df.low.values, df.close.values, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
            df['k'] = k
            df['d'] = d
            wr = talib.WILLR(df.high.values, df.low.values, df.close.values, timeperiod=14)
            df['wr'] = wr
            rsi = talib.RSI(df.close.values, timeperiod=14)
            df['rsi'] = rsi
            cr100 = talib.ROCR100(df.close.values, timeperiod=10)
            df['cr100'] = cr100
            adx = talib.ADX(df.high.values, df.low.values, df.close.values, timeperiod=14)
            df['adx'] = adx
            dx = talib.DX(df.high.values, df.low.values, df.close.values, timeperiod=14)
            df['dx'] = dx
            cci = talib.CCI(df.high.values, df.low.values, df.close.values, timeperiod=14)
            df['cci'] = cci
            upperband, middleband, lowerband = talib.BBANDS(df.close.values, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
            df['upperband'] = upperband
            df['middleband'] = middleband
            df['lowerband'] = lowerband
            sar = talib.SAR(df.high.values, df.low.values, acceleration=0, maximum=0)
            df['sar'] = sar
            ad = talib.ADOSC(df.high.values, df.low.values, df.close.values, df.volume.values, fastperiod=3, slowperiod=10)
            df['ad'] = ad
            obv = talib.OBV(df.close.values, df.volume.values)
            df['obv'] = obv
            atr = talib.ATR(df.high.values, df.low.values, df.close.values, timeperiod=14)
            df['atr'] = atr
            pass
        pass

    def run(self):
        '''
        strategy goes here
        Returns:
        '''
        # dataFrames = self.datas.values()
        for index in self.ticks:
            try:
                for df in self.datas.values():
                    row = df.ix[index]
                    if len(row) > 3:
                        self.acount.update(code=row.code, price=row.close)
                        if self.begin is None:
                            self.begin = index
                        self.end = index
                for df in self.datas.values():
                    row = df.ix[index]
                    if len(row) > 3:
                        order = self.handle_data(
                            tick=index, data=df.ix[:index], row=row)
            except Exception as e:
                if not isinstance(e, KeyError):
                    pass
                # traceback.print_exc()
                # ignore
                pass
            self.p += 1

    def baseline(self):
        '''
        等权买入并持有
        '''
        b = 0.
        e = 0.
        for data in self.datas.values():
            b += data.ix[self.begin].close
            e += data.ix[self.end].close
            print self.begin, data.ix[self.begin].close
            print self.end, data.ix[self.end].close
        n = len(self.datas)
        print b/n, e/n
        return (e/n - b/n) / b/n

    def handle_data(self, tick, data, row):
        '''
        处理当天的数据,根据策略给出的信号，发错买入或卖出指令。买入卖出量由仓位管理模块控制。
        Args:
            tick: 当天日期yyyy-mm-dd
            data: 从开始日期到当前日期的全部数据
            row: 当前日期（当日）数据

        Returns:

        '''
        yestoday = self.get_one_data(data, -1)
        # if row.ma5 > row.ma10 and row.ma10 > row.ma20 and yestoday.ma5 < yestoday.ma10:
        #     self.order.order(tick, 1, row.code, row.close)
        # if row.ma5 < row.ma10 and yestoday.ma5 > yestoday.ma10:
        #     self.order.order(tick, 2, row.code, row.close)

        # if row.close > row.sar and yestoday.close < row.sar:
        #     self.order.order(tick, 1, row.code, row.close)
        # if row.close < row.sar and yestory.close > row.sar:
        #     self.order.order(tick, 2, row.code, row.close)

        if row.macd > 0:
            self.order.order(tick, 1, row.code, row.close)
        if row.close > row.upperband:
        if row.ma5 > row.ma10 :
            self.order.order(tick, 1, row.code, row.close)
        if row.ma5 < row.ma10:
            self.order.order(tick, 2, row.code, row.close)
        pass

    def get_one_data(self, data, i):
        if i < 0:
            if i < 0 and self.p + i >= 0:
                return data.ix[self.ticks[self.p + i]]
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

    def baseline(self, begin, end):
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

    a = abstrictStrategy(stock_pool=['600036','000001'], start='2015-01-01', end='2016-12-01')

    # import matplotlib.pyplot as plt
    # import pandas as pd
    # import matplotlib
    # matplotlib.style.use('ggplot')
    # t = pd.DataFrame(index=a.datas['600036'].index)
    # t['c'] = a.datas['600036'].close
    # t['sar'] = a.datas['600036'].sar
    # print t.tail()
    # plt.figure()
    # t.plot()


    stock_pool=['600636'], start='2015-01-01', end='2016-08-01')
    a.run()
    print a.acount.cash, a.acount.get_value(), a.acount.get_assets(), a.acount.get_position_profit()
    # print a.order.net
    print sum([i[3] for i in a.order.net])
    print a.acount.stocks
    n = len([i[3] for i in a.order.net if i[3] > 0])
    m = len(a.order.net)
    # print '%d/%d=%f' % (n, m, n / float(m))
    print a.metrics.baseline(a.begin, a.end)
    print a.baseline()
    print (a.acount.get_assets() - a.acount.initail_cash) / a.acount.initail_cash

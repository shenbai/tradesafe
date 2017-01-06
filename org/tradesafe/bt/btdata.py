# coding: utf-8
__author__ = 'tack'

from org.tradesafe.data.history_data import HistoryData
from datetime import datetime, timedelta
import traceback
import sys
from math import *
import talib


class BtData(object):
    '''
    Back test Data
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
        pass


    def indicator(self, **kwargs):
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
            upperband, middleband, lowerband = talib.BBANDS(df.close.values, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
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
            df['ma5'] = talib.MA(df.close.values, timeperiod=5)
            df['ma10'] = talib.MA(df.close.values, timeperiod=10)
            df['ma30'] = talib.MA(df.close.values, timeperiod=30)
            df['ma60'] = talib.MA(df.close.values, timeperiod=60)
            df['beta'] = talib.BETA(df.high.values, df.low.values, timeperiod=5)
            df['l_angle'] = talib.LINEARREG_ANGLE(df.close.values, timeperiod=14)
            df['l_intercept'] = talib.LINEARREG_INTERCEPT(df.close.values, timeperiod=14)
            df['l_slope'] = talib.LINEARREG_SLOPE(df.close.values, timeperiod=14)
            df['stddev'] = talib.STDDEV(df.close.values, timeperiod=5, nbdev=1)
            df['tsf'] = talib.TSF(df.close.values, timeperiod=14)


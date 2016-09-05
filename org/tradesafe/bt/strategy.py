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


class Order(object):

    def __init__(self, acount=None, **kwargs):
        self.acount = acount
        self.net = []

    def order(self, date=None, bs=1, code=None, price=0., **kwargs):
        """

        Args:
            date: date
            bs: 1: buy, 2: sell
            code: code
            price: 成交价格
            commission: 佣金比例
            **kwargs:

        Returns:
        """
        if bs == 1:
            # 可用现金=总资产*最大仓位-市直
            availableCash = self.acount.get_assets() * self.acount.maxPosition - \
                self.acount.get_value()
            if availableCash > 0:
                # 检查要买的股票是否在持有，如持有则本次买入不能超过单只最大仓位
                if code in self.acount.stocks:
                    # 买一只股票可用的最大现金=总资产*单只股票最大仓位-该股票市直
                    cashOneStock = min(availableCash, self.acount.get_assets() *
                                       self.acount.maxPositionPerShare - self.acount.stocks.get(code).get_value())
                    num = self.buyNum(cashOneStock, price)
                    self.opExec(code, num, price, bs, date)
                else:
                    cashOneStock = min(
                        availableCash, self.acount.get_assets() * self.acount.maxPositionPerShare)
                    num = self.buyNum(cashOneStock, price)
                    self.opExec(code, num, price, bs, date)
        if bs == 2:
            # 可卖出金额=当前持仓-最小持仓
            # canSellCash = self.acount.get_value() - self.acount.get_assets() * \
            #     self.acount.minPosition
            # if canSellCash > 0 and code in self.acount.stocks:
            #     num = self.sellNum(canSellCash, price,
            #                        self.acount.stocks.get(code).num)
            #     self.opExec(code, num, price, bs, date)
            if code in self.acount.stocks:
                self.opExec(code, self.acount.stocks.get(
                    code).num, price, bs, date)

    def sellNum(self, cash, price, totalNum):
        num = floor(cash / (price * (1 + self.acount.sellCommission))) / 100
        num = int(num) * 100
        return min(totalNum, num)

    def buyNum(self, cash, price):
        num = floor(cash / (price * (1 + self.acount.buyCommission))) / 100
        return int(num) * 100

    def opExec(self, code, num, price, bs=1, date=None):
        # print '#1', code, num, price, bs, date
        # print '#2', self.acount.stocks
        if bs == 1 and num > 0:
            amount = num * price
            commissions = max(
                amount * self.acount.buyCommission, self.acount.minFee)
            cost = amount + commissions
            self.acount.cash -= cost

            if code in self.acount.stocks:
                p = Position(code=code, cost=cost, num=num, price=price)
                self.acount.stocks[code] = self.acount.stocks[code].add(p)
            else:
                self.acount.stocks[code] = Position(
                    code=code, cost=cost, num=num, price=price, date=datetime.now())
            print '%s, %s b at price %f, num %d, cost %f, amount %f, fee %f, asset %f, cash %f, value %f' % (date, code, price, num, cost, amount, commissions, self.acount.get_assets(), self.acount.cash, self.acount.get_value())
            return date, code, price, num, cost, amount, commissions, bs

        if bs == 2 and num > 0:
            p = self.acount.stocks.get(code)
            amount = num * price
            cost = p.cost * (float(num) / float(p.num))
            commissions = max(
                amount * self.acount.sellCommission, self.acount.minFee)
            self.acount.cash += (amount - commissions)
            if num == p.num:
                self.acount.stocks.pop(code)
            elif num < p.num:  # 更新持仓成本
                n = Position(code=code, cost=amount, num=num, price=price)
                self.acount.stocks[code].sub(n)
            else:
                raise Exception(
                    'sell num error for code=%s, num=%d' % (code, num))
            print '%s, %s s at price %f, num %d, cost %f, amount %f, fee %f,net %f, asset %f, cash %f, value %f' % (date, code, price, num, cost, amount, commissions, amount - cost - commissions, self.acount.get_assets(), self.acount.cash, self.acount.get_value())
            self.net.append((date, amount, cost, amount - cost - commissions))
            print 'loss', sum([i[3] for i in a.order.net])
            print 'paper', self.acount.get_paper()
            return date, code, price, num, cost, amount, commissions, bs
        # print '#3', self.acount.stocks


class Acount(object):

    def get_assets(self):
        return self.cash + self.get_value()

    def __init__(self, id=None, passwd=None, cash=100000, maxPosition=1., minPosition=0., maxPositionPerShare=1., **kwargs):
        '''
        账户管理
        Args:
            id:
            passwd:
            cash: 初始可用资金
            maxPosition: 最大仓位（0-1）
            minPostion: 最小仓位（0-1）
            maxPostionPerShare: 单只股票最大仓位（0-1）
            **kwargs:
                mount:总资金
                buyCommission：买入佣金比例
                sellCommission：卖出佣金比例
                minFee:最小费用（5）
                socks:当前持仓证券
                stockPool:自选股票池     -- delete
                strategies:可应用的策略   -- delete
        '''
        self.id = id
        self.passwd = passwd
        self.initail_cash = cash
        self.cash = cash
        self.maxPosition = maxPosition
        self.minPosition = minPosition
        self.maxPositionPerShare = maxPositionPerShare
        self.stocks = {}
        self.buyCommission = kwargs.get('buyCommission', 0.001)
        self.sellCommission = kwargs.get('sellCommission', 0.003)
        self.minFee = kwargs.get('minFee', 5)
        pass

    def update(self, code=None, price=None):
        if code is not None and price is not None:
            if code in self.stocks:
                self.stocks[code].update(price)
        pass

    def get_value(self):
        '''
        value of acount
        '''
        value = 0.
        for p in self.stocks.values():
            value += p.get_value()
        return value

    def get_paper(self):
        paper = 0.
        for p in self.stocks.values():
            paper += p.get_paper()
        return paper


class OrderHistory(object):

    def __init__(self):
        pass

    def record(self, order=None):
        if order:
            # TODO 记录数据库/持仓、交易等等。。
            pass


class Position(object):

    def __init__(self, **kwargs):
        '''
        持仓
        Args:
            **kwargs:
                code:
                cost:
                price:
                num:
                date:
        '''
        self.code = kwargs.get('code')
        self.cost = kwargs.get('cost')
        self.num = kwargs.get('num')
        self.price = kwargs.get('price')
        self.date = kwargs.get('date')
        pass

    def add(self, position=None):
        '''
        加仓
        '''
        if position is not None and position.code == self.code:
            self.cost += position.cost
            self.num += position.num
            return self

    def sub(self, position=None):
        '''
        减持
        '''
        if position is not None and position.code == self.code:
            self.cost -= position.cost
            self.num -= position.num
            return self

    def update(self, price=None):
        '''
        update price
        '''
        if price is not None:
            self.price = price

    def get_value(self):
        '''
        value
        '''
        return self.price * self.num

    def get_paper(self):
        '''
        paper loss, paper gain
        '''
        return self.get_value() - self.cost

    def __repr__(self):
        return 'code=%s,cost=%f,price=%f,num=%d,value=%f,date=%s' % (self.code, self.cost, self.price, self.num, self.get_value(), self.date)


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

    a = abstrictStrategy(
        stock_pool=['600636'], start='2015-01-01', end='2016-08-01')
    a.run()
    print a.acount.cash, a.acount.get_value(), a.acount.get_assets(), a.acount.get_paper()
    # print a.order.net
    print sum([i[3] for i in a.order.net])
    print a.acount.stocks
    n = len([i[3] for i in a.order.net if i[3] > 0])
    m = len(a.order.net)
    print '%d/%d=%f' % (n, m, n / float(m))
    print a.metrics.baseline(a.begin, a.end)
    print a.baseline()
    print (a.acount.get_assets() - a.acount.initail_cash) / a.acount.initail_cash

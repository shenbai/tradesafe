# coding:utf-8
from datetime import datetime, timedelta
import traceback
import sys
from math import *


class abstrictStrategy(object):
    '''
    strategy
    '''

    def __init__(self, datas={}, **kwargs):
        self.datas = datas
        start_date = kwargs.get('start')
        end_date = kwargs.get('end')
        if start_date is None or end_date is None:
            raise Exception('no start,end time set')
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
        self.order = Order(self.acount)

    def run(self):

        # dataFrames = self.datas.values()
        for index in self.ticks:
            try:
                for df in self.datas.values():
                    row = df.ix[index]
                    if len(row) > 3:
                        self.acount.update(code=row.code, price=row.close)
                for df in self.datas.values():
                    row = df.ix[index]
                    if len(row) > 3:
                        order = self.handle_data(
                            tick=index, data=df.ix[:index], row=row)
            except Exception as e:
                # if not isinstance(e, KeyError):
                    # pass
                # traceback.print_exc()
                # ignore
                pass

    def handle_data(self, tick, data, row):
        '''
        处理当天的数据,根据策略给出的信号，发错买入或卖出指令。买入卖出量由仓位管理模块控制。
        Args:
            tick: 当天日期yyyy-mm-dd
            data: 从开始日期到当前日期的全部数据
            row: 当前日期（当日）数据

        Returns:

        '''
        # print '#', row.ma10
        # print '#0', data[0].ma10
        # print '#1', data[-2:-1].ma10
        # print '#2', data[-2].ma10
        yestoday = self.get_one_data(data, -2)
        print '1', yestoday.date, yestoday.ma5 > yestoday.ma10
        print '2', row.date, row.ma5 > row.ma10
        if row.ma5 > row.ma10 and yestoday.ma5 < yestoday.ma10:
            self.order.order(tick, 1, row.code, row.close)
        if row.ma5 < row.ma10 and yestoday.ma5 > yestoday.ma10:
            self.order.order(tick, 2, row.code, row.close)
        pass

    def get_one_data(self, data, i):
        if i < 0:
            if i == -1:
                return data[i:]
            if i < -1:
                return data[i:i + 1]
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
                                       self.acount.maxPositionPerShare
                                       - self.acount.stocks.get(code).get_value())
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
                n = Position(code=code, cost=cost, num=num, price=price)
                self.acount.stocks[code].sub(n)
            else:
                raise Exception(
                    'sell num error for code=%s, num=%d' % (code, num))
            print '%s, %s s at price %f, num %d, cost %f, amount %f, fee %f,net %f, asset %f, cash %f, value %f' % (date, code, price, num, cost, amount, commissions, amount - cost - commissions, self.acount.get_assets(), self.acount.cash, self.acount.get_value())
            self.net.append((date, amount, cost, amount - cost - commissions))
            print sum([i[3] for i in a.order.net])
            print self.acount.get_paper()
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

if __name__ == '__main__':
    from org.tradesafe.data.history_data import HistoryData
    hd = HistoryData()
    df1 = hd.get_history_data(
        code='002084', startDate='2016-01-01', endDate='2016-08-01')
    df2 = hd.get_history_data(
        code='600518', startDate='2016-01-01', endDate='2016-08-01')
    # print df2.head()
    a = abstrictStrategy(
        datas={'22': df1, '33': df2}, start='2016-01-01', end='2016-08-01')
    a.run()
    print a.acount.cash, a.acount.get_value(), a.acount.get_assets(), a.acount.get_paper()
    # print a.order.net
    print sum([i[3] for i in a.order.net])
    print a.acount.stocks
    print len([i[3] for i in a.order.net if i[3] > 0]) / float(len(a.order.net))

# coding:utf-8
from datetime import datetime,timedelta
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
        if kwargs.has_key('acount'):
            self.acount = kwargs.get('acount')
        else:
            self.acount = Acount(maxPosition=0.8, maxPositionPerShare=0.2)
        self.order = Order(self.acount)

    def run(self):
        # dataFrames = self.datas.values()
        for index in self.ticks:
            try:
                for df in self.datas.values():
                    row = df.ix[index]
                    if len(row) > 3:
                        order = self.handle_data(tick=index, data=df.ix[:index], row=row)

            except:
                # traceback.print_exc()
                # ignore
                pass
        for df in self.datas.values():
            df

    def handle_data(self, tick, data, row):
        '''
        处理当天的数据,根据策略给出的信号，发错买入或卖出指令。买入卖出量由仓位管理模块控制。
        Args:
            tick: 当天日期yyyy-mm-dd
            data: 从开始日期到当前日期的全部数据
            row: 当前日期（当日）数据

        Returns:

        '''
        if row.ma5 > row.ma20:
            self.order.order(tick, 1, row.code, row.close)
        if row.ma5 < row.ma10:
            self.order.order(tick, 2, row.code, row.close)
        pass

class Order(object):

    def __init__(self, acount=None, **kwargs):
        self.acount = acount

        pass

    def order(self, date=None, bs=1,code=None, price=0., **kwargs):
        """

        Args:
            date: date
            bs: 1: buy, 2: sell
            code: code
            price: 成交价格
            num: 成交数量
            commission: 佣金比例
            **kwargs:

        Returns:
        """
        if bs == 1:
            # 可用现金=总资产*最大仓位-市直
            availableCash = (self.acount.cash + self.acount.value) * self.acount.maxPosition - self.acount.value
            if availableCash > 0:
                # TODO 检查要买的股票是否在持有，如持有则本次买入不能超过单只最大仓位
                if self.acount.stocks.has_key(code):
                    # 买一只股票可用的最大现金=总资产*单只股票最大仓位-该股票市直
                    cashOneStock = min(availableCash, (self.acount.cash + self.acount.value) *\
                                  self.acount.maxPositionPerShare\
                                  - self.acount.stocks.get(code).num * self.acount.stocks.get(code).price)
                    num = self.buyNum(cashOneStock, price)
                    self.opExec(code, num, price, bs, date)
                else:
                    cashOneStock = min(availableCash, (self.acount.cash + self.acount.value) * self.acount.maxPositionPerShare)
                    num = self.buyNum(cashOneStock, price)
                    self.opExec(code, num, price, bs, date)
        if bs == 2:
            #可卖出金额=当前持仓-最小持仓
            canSellCash = self.acount.value - (self.acount.cash + self.acount.value) * self.acount.minPosition
            if canSellCash > 0 and self.acount.stocks.has_key(code):
                num = self.sellNum(canSellCash, price, self.acount.stocks.get(code).num)
                self.opExec(code, num, price, bs, date)
            pass

    def sellNum(self, cash, price, totalNum):
        num = (floor(cash / (price + self.acount.buyCommission)) / 100)
        num = int(num) * 100
        return min(totalNum, num)

    def buyNum(self, cash, price):
        num = (floor(cash / (price + self.acount.buyCommission)) / 100)
        return int(num) * 100

    def opExec(self, code, num, price, bs=1, date=None):
        if bs == 1 and num > 0:
            amount = num * price
            commissions = max(amount * self.acount.buyCommission, self.acount.minFee)
            self.acount.cash = self.acount.cash - amount - commissions
            self.acount.value = self.acount.value + amount
            # TODO 更新持仓成本
            self.acount.stocks[code] = Position(code=code, cost=price, price=price, num=num, date=datetime.now())
            print '%s, buy code(%s), %d, at price %f, amount %f, fee %f' % (date, code, num, price, amount, commissions)

        if bs == 2 and num > 0:
            p = self.acount.stocks.get(code)
            amount = num * price
            net = amount - num * p.cost
            commissions = max(amount * self.acount.buyCommission, self.acount.minFee)
            self.acount.cash = self.acount.cash + amount - commissions
            self.acount.value = self.acount.value - amount
            print '%s, sell code(%s), %d, at price %f,cost %f amount %f, fee %f, net %f' % (date, code, num, price, p.cost, amount, commissions, net)
            if num == p.num:
                self.acount.stocks.pop(code)
            elif num < p.num:
                p.num = p.num - num
                self.acount.stocks[code] = p
            else:
                raise Exception('sell num error for code=%s, num=%d' % (code, num))

class Acount(object):

    def __init__(self,id=None,passwd=None, cash=100000, maxPosition=1., minPosition=0., maxPositionPerShare=1., **kwargs):
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
                value:持仓市直
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
        self.value = 0.
        self.maxPosition = maxPosition
        self.minPosition = minPosition
        self.maxPositionPerShare = maxPositionPerShare
        self.stocks = {}
        self.buyCommission = kwargs.get('buyCommission', 0.001)
        self.sellCommission = kwargs.get('sellCommission', 0.003)
        self.minFee = kwargs.get('minFee', 5)
        pass

class OrderHistory(object):

    def __init__(self):
        pass

    def record(self, order=None):
        if order:
            # TODO 记录数据库
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
        self.price = kwargs.get('price')
        self.num = kwargs.get('num')
        self.date = kwargs.get('date')
        pass

    def __repr__(self):
        return 'code=%s,cost=%f,price=%f,num=%d,date=%s' % (self.code,self.cost,self.price,self.num,self.date)

if __name__ == '__main__':
    from org.tradesafe.data.history_data import HistoryData
    hd = HistoryData()
    df1 = hd.get_history_data(code='600622', startDate='2016-01-01', endDate='2016-08-01')
    # df2 = hd.get_history_data(code='600633', startDate='2016-01-01', endDate='2016-08-01')
    # print df2.head()
    a = abstrictStrategy(datas={'22':df1}, start='2016-01-01', end='2016-08-01')
    a.run()
    print a.acount.cash, a.acount.value, a.acount.cash + a.acount.value
    print a.acount.stocks
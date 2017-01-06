# coding: utf-8
__author__ = 'tack'

class Order(object):

    def __init__(self, code, num,hold_num, cost_price, market_price, commission, date, cmd):
        '''
        Args:
            code: stock code
            cost_price: cost price
            market_price: market price
            commission: commission
            num: num
            hold_num: hold num
            date: date
            cmd: buy|sell
        '''
        self.code = code
        self.num = num
        self.hold_num = hold_num
        self.date = date
        self.commission = commission
        self.cost_price = cost_price
        self.market_price = market_price
        self.cost = self.cost_price * num + commission
        self.cmd = cmd
        if (self.hold_num == 0 and 'sell' == self.cmd):
            self.profit = (self.market_price - self.cost_price) * num - self.commission
        else:
            self.profit = 0 - self.commission


    def __repr__(self):
        return 'cmd=%s, code=%s,cost=%f,cost_price=%f, market_price=%f,num=%d, hold_num=%d, commission=%f, profit=%f, date=%s' % (self.cmd, self.code, self.cost, self.cost_price,self.market_price, self.num,self.hold_num, self.commission,self.profit, self.date)

class OrderHistory(object):
    def __init__(self):
        self._ohs = {}

    def update(self, order):
        '''
        when the market close, update positions
        :param order:
        :return:
        '''
        if order.code in self._ohs:
            self._ohs[order.code].append(order)
        else:
            self._ohs[order.code] = [order]

    def get_history(self, code):
        return self._ohs.get(code, None)

    def get_total_profit(self, code):
        if code not in self._ohs:
            return 0.
        profit = 0.
        for o in self._ohs[code]:
            profit += o.profit
        return profit
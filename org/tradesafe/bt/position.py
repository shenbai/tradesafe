# coding: utf-8
__author__ = 'tack'

class Position(object):
    '''
    position
    '''
    def __init__(self, code, num, price, commission, date):
        '''
        Args:
            code: stock code
            price: cost price
            commission: commission
            num: num
            date: date
        '''
        self.code = code
        self.num = num
        self.date = date
        self.commission = commission
        self.cost = price * self.num + commission
        self.cost_price = self.cost / self.num
        self.market_price = price

    def add(self, position):
        '''
        buy some
        '''
        if position is None:
            raise Exception('position is none')
        if position.code != self.code:
            raise Exception('add op can not apply on different stocks')
        self.cost += position.cost
        self.num += position.num
        self.cost_price = self.cost / self.num
        self.market_price = position.market_price
        return True, 'done'

    def sub(self, position=None):
        '''
        sell some
        '''
        if position is None:
            raise Exception('position is none')
        if position.code != self.code:
            raise Exception('sub op can not apply on different stocks')
        if position.num <= self.num:
            self.cost -= position.get_market_value()   # total cost - market value
            self.num -= position.num
            self.update(market_price=position.market_price)
            if self.num == 0:
                self.cost_price = 0.
                return True, 'done'
            self.cost_price = self.cost / self.num

            return True, 'done'
        else:
            return False, 'no enough stocks to sell'

    def update(self, market_price=None):
        '''
        update market price
        '''
        self.market_price = market_price

    def get_cost_value(self):
        '''
        value
        '''
        # return self.cost_price * self.num
        return self.cost

    def get_market_value(self, market_price=None):
        '''
        get market value of the position
        '''
        if market_price is not None:
            self.market_price = market_price
        if self.market_price is None:
            raise Exception('you need to update market price.')
        return self.market_price * self.num

    def get_profit(self):
        '''
        paper loss, paper gain
        '''
        return self.get_market_value() - self.cost

    def __repr__(self):
        return 'code=%s,cost=%f,cost_price=%f, market_price=%f,num=%d,value=%f,profit=%f,date=%s' % (self.code, self.cost, self.cost_price,self.market_price, self.num, self.get_market_value(), self.get_profit(), self.date)

    def get(self):
        return (self.code, self.num, self.cost_price, self.date)


class PosstionHistory(object):
    '''
    history of position
    '''
    def __init__(self):
        self.phs = {}

    def update(self, position):
        '''
        when the market close, update positions
        :param position:
        :return:
        '''
        if position.code in self.phs:
            self.phs[position.code].append(position)
        else:
            self.phs[position.code] = [position]

    def get_history(self, code):
        return self.phs.get(code, None)


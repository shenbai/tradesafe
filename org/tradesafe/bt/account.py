# coding:utf-8
__author__ = 'tack'
from org.tradesafe.bt.log import logging as log
from org.tradesafe.bt.position import Position
from org.tradesafe.bt.position import PosstionHistory
from org.tradesafe.bt.order import Order
from org.tradesafe.bt.order import OrderHistory
from math import *
import copy

class Account(object):
    '''
    account management
    '''

    def __init__(self, id=None, passwd=None, cash=100000, max_position=1., min_position=0., max_position_per_stock=1., **kwargs):
        '''
        Args:
            id:
            passwd:
            cash: initial cash
            maxPosition: max position（0-1）
            minPosition: min position（0-1）
            maxPositionPerStock: max position per stock（0-1）
            **kwargs:
                buyCommission：commission ratio on buy
                sellCommission：commission ratio on sell
                minFee:min fee（5）,when trading fee less then 5,take 5
        '''
        self.id = id
        self.password = passwd
        self.initial_cash = cash
        self.cash = cash
        self.max_position = max_position
        self.min_position = min_position
        self.max_position_per_stock = max_position_per_stock

        self.buy_commission = kwargs.get('buy_commission', 0.003)
        self.sell_commission = kwargs.get('sell_commission', 0.003)
        # self.max_buy_mount = kwargs.get('max_buy_mount', 10000)
        self.min_fee = kwargs.get('minFee', 5)
        self.positions = {}
        self.history_positions = PosstionHistory()
        self.history_orders = OrderHistory()
        self.history_assets = []

    def get_assets(self):
        '''
        assets = cash + market value
        :return: assets
        '''
        return self.cash + self.get_market_value()

    def is_hold(self, code):
        return code in self.positions

    def buy_restriction_filter(self, data):
        is_up_limit = True # can't buy by price great then limit price
        if len(data.index) >= 2:
            r = (data[-1:].close[0] - data[-2:].close[0]) / data[-2:].close[0]
            is_up_limit = r >= 0.095
        return is_up_limit


    def sell_restriction_filter(self, data):
        is_low_limit = True # can't sell if price go down to low limit price
        if len(data.index) >= 2:
            is_low_limit = (data[-1:].close[0] - data[-2:].close[0]) / data[-2:].close[0] <= -0.095
        return is_low_limit


    def buy(self, code, price, num=100, date=None):
        '''
        buy security
        :param code:
        :param price:
        :param num:
        :param date:
        :return: result(true|false), position, message
        '''
        # total available cash = total assets * max position - total market value
        total_available_cash = self.get_assets() * self.max_position - self.get_market_value()
        if total_available_cash <= 0:
            log.warning('total available cache less then 0, max position ratio is %f, current position ratio is %f' % (self.max_position, self.get_market_value()/self.get_assets()))
            return False, None, 'do not enough available cash'
        else:
            # if we hold this stock, market value can't exceed max_position_per_stock * assets
            current_market_value_of_this_position = 0.
            if self.is_hold(code):
                current_market_value_of_this_position += self.positions[code].get_market_value()
            available_cash = self.get_assets() * self.max_position_per_stock - self.get_market_value() - current_market_value_of_this_position
            if available_cash >= 0 and self.cash >= available_cash:
                can_buy_num = int(floor(available_cash / (price * (1 + self.buy_commission)) / 100) * 100)
                buy_num = min(num, can_buy_num)
                if buy_num < 100:
                    return False, None, 'buy num should be n times of 100'
                buy_position = self._send_buy_cmd(code, buy_num, date, price=price)
                if buy_position is None:
                    return False, None, 'send_buy_cmd error, return position is None'
                if code in self.positions:
                    r, msg = self.positions[code].add(buy_position)
                    if r:
                        self.history_orders.update(Order(code,buy_num,self.positions[code].num, price, price, buy_num*price*self.buy_commission,date,'buy'))
                    return r, buy_position, msg
                else:
                    self.positions[code] = buy_position
                    self.history_orders.update(Order(code,buy_num,self.positions[code].num, price, price, buy_num*price*self.buy_commission,date,'buy'))
                    return True, buy_position, 'open a position'
            else:
                return False,None, 'not enough available cash for %s' % code

    def _send_buy_cmd(self, code, num, date, **kwargs):
        if 'price' in kwargs:
            price = kwargs.get('price')
            # simulate real trade
            commission = price * num * self.buy_commission
            self.cash -= num * price + commission
            return Position(code=code, num=num, price=price,commission=commission, date=date)
        else:
            raise Exception('back test only support limit price trade')


    def sell(self, code, price, num=100, date=None):
        '''
        sell security
        :param code:
        :param price:
        :param num:
        :param date:
        :return: result(true|false), messages
        '''
        min_position_value = self.get_assets() * self.min_position
        current_position_value = self.get_market_value()
        if current_position_value <= min_position_value:
            return False, 'refuse to sell security. keep at lest min_position %f' % self.min_position
        else:
            if code in self.positions:
                previous_cost_price = self.positions[code].cost_price
                sell_num = min(num, self.positions[code].num)
                sell_position = self._send_sell_cmd(code, sell_num, date, price=price)
                r, msg = self.positions[code].sub(sell_position)
                if r:
                    self.history_orders.update(Order(code,sell_num,self.positions[code].num, previous_cost_price, price, sell_num*price*self.sell_commission,date,'sell'))
                    if self.positions[code].num == 0:
                        del self.positions[code]
                return r, sell_position, msg
            else:
                return False, None, 'do not hold this stock ,can not sell'

    def _send_sell_cmd(self, code, num, date, **kwargs):
        if 'price' in kwargs:
            price = kwargs.get('price')
            # simulate real trade
            commission = price * num * self.sell_commission
            self.cash += price * num - commission
            return Position(code=code, num=num, price=price, commission=commission, date=date)
        else:
            raise Exception('back test only support limit price trade')

    def get_market_value(self):
        '''
        value of acount
        '''
        value = 0.
        for p in self.positions.values():
            value += p.get_market_value()
        return value

    def get_position_profit(self):
        '''
        :return: profit
        '''
        paper = 0.
        for p in self.positions.values():
            paper += p.get_profit()
        return paper

    def get_profit(self):
        '''
        get total profit
        :return:
        '''
        return self.get_assets() - self.initial_cash

    def update_price_of_position(self, code, price, date):
        '''
        update price of security every day,also update history positions very tick
        :param code:
        :param price:
        :param date:
        :return:
        '''
        # update assets every day
        self.history_assets.append((date, self.get_assets(), self.cash, self.get_market_value(), (self.get_assets() - self.initial_cash)/ self.initial_cash))
        # update position information every day
        if code in self.positions:
            self.positions[code].update(market_price=price)
            p = copy.deepcopy(self.positions[code])
            p.date = date
            self.history_positions.update(p)

    def __repr__(self):
        return 'assets=%f, cash=%f, market_value=%f,profit=%f, position_profit=%f, positions=%s' %(self.get_assets(), self.cash, self.get_market_value(),self.get_profit(), self.get_position_profit(), str(self.positions))


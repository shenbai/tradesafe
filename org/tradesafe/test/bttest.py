# coding:utf-8
__author__ = 'zhaoziqiang1'

import unittest
import datetime
import time
from org.tradesafe.bt.account import Account
from org.tradesafe.bt.position import Position


class AccountTest(unittest.TestCase):

    def testPosition(self):
        d = time.strftime('%Y-%m-%d')
        time.time()
        p = Position(code='00', num=1000, price=10, commission=1000*10*0.003, date=d)
        self.assertEqual(1000* 10 + 1000 * 10 * 0.003, p.cost)
        self.assertEqual(p.cost, p.get_cost_value())
        p.update(10.2)
        print p
        add_p = Position(code='00', num=1000, price=11, commission=1000*11*0.003, date=d)
        p.add(add_p)
        print add_p
        print p
        sub_p = Position(code='00', num=1000, price=12, commission=1000*11*0.003, date=d)
        p.update(18)
        p.sub(sub_p)
        print p

        from org.tradesafe.bt.log import logging as log
        log.error('hahaddd')

    def testAccount(self):
        d = time.strftime('%Y-%m-%d')
        a = Account()
        a.buy('00',10., num=1000, date=d)
        print(a)
        a.sell('00', 11., num=500, date=d)
        print a
        a.sell('00', 12., num=500, date=d)
        print a
        a.sell('00', 11., num=-500, date=d)
        print a
        import talib


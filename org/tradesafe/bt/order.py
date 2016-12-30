# coding: utf-8
__author__ = 'tack'

class Order(object):

    def __init__(self, acount=None, **kwargs):
        self.acount = acount
        self.net = []

class OrderHistory(object):

    def __init__(self):
        pass

    def record(self, order=None):
        if order:
            # TODO 记录数据库/持仓、交易等等。。
            pass


# coding:utf-8

import pandas as pd
import talib


class Indicator(object):
    def __init__(self, stock_code, history):
        self.stock_code = stock_code
        self.history = history

    def __getattr__(self, item):
        def talib_func(*args, **kwargs):
            str_args = ''.join(map(str, args))
            if self.history.get(item + str_args) is not None:
                return self.history
            func = getattr(talib, item)
            res_arr = func(self.history['close'].values, *args, **kwargs)
            self.history[item + str_args] = res_arr
            return self.history

        return talib_func
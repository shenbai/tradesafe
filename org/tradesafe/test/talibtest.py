# coding:utf-8

import talib
import numpy as np
from talib.abstract import *
close = np.random.random(100)
output = talib.SMA(close, timeperiod=5)
# print output
from org.tradesafe.db import sqlite_db as db
import pandas as pd
import numpy as np

# note that all ndarrays must be the same length!

inputs = {

    'high': np.random.random(100),
    'open': np.random.random(100),
    'low': np.random.random(100),
    # 'close': np.random.random(100),
    'volume': np.random.random(100)
}
output = SMA(inputs, timeperiod=25, price='open')
# print CCI(inputs,  price='high')
# print output

conn = db.get_history_data_db('D')
df = pd.read_sql_query(
    "select * from history_data where code='%s' order by date([date]) asc" % '600022', conn)
df['sma15'] = talib.SMA(df['high'].values, timeperiod=15)
print df.head(30)
if __name__ == '__main__':
    pass
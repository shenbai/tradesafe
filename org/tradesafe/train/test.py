# coding:utf-8

from org.tradesafe.data.history_data import HistoryData
from datetime import datetime, date, timedelta
import os

from pandas.io import sql
from org.tradesafe.utils import utils
from org.tradesafe.data.index_code_conf import indices
from org.tradesafe.conf import config
from org.tradesafe.utils.memo import Memo
from org.tradesafe.db import sqlite_db as db
import pandas as pd
import tushare as ts
from urllib2 import Request, urlopen
import demjson

hd = HistoryData()
df = hd.get_history_data_day()
lags = 20
# df['target'] = None
# for i in range(0, len(df)-5):
#     df.loc[i, 'target'] = max(df.loc[i:i+lag,'close'])
#     if i>10000:
#         break
# print df.head(20)
# print df['close'].shift(5)
tslag = pd.DataFrame(index=df.index)
# for i in xrange(0, lags):
#     print i
#     tslag['Lag%s' % str(i + 1)] = df["close"].shift(i + 1)
df['target'] = df['close'].shift(5)

import sklearn

from pandas.io.data import DataReader
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.qda import QDA

# print len(df)
split = 780000
df=df[df['target']>0]
X_train = df.ix[0:split,'code':'turnover']
y_train = df.ix[0:split,'target']
X_test = df.ix[split:,'code':'turnover']
y_test = df.ix[split:,'target']

lr = LogisticRegression()
lr.fit(X_train, y_train)

pred = model.predict(X_test)

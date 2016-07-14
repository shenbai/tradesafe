# coding:utf-8

from org.tradesafe.data.history_data import HistoryData
from datetime import datetime, date, timedelta
import time
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
from sklearn.metrics import explained_variance_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor
import sklearn
from pandas.io.data import DataReader
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.qda import QDA
import cPickle as pickle

hd = HistoryData()
# df = hd.get_history_data_day()
conn = db.get_history_data_db('D')
df = None
try:
    df = pd.read_sql_query(
        'select * from history_data where code="600568" order by code, date([date]) asc', conn)
    print len(df)
except Exception, e:
    print e
codes = hd.get_all_stock_code()
lags = 1
# print len(df)
split = 0.9
# df = df[df['target'] > 0]
# X_train = df.ix[0:split, 'code':'turnover']
# y_train = df.ix[0:split, 'target']
# X_test = df.ix[split:, 'code':'turnover']
# y_test = df.ix[split:, 'target']
# lr = LogisticRegression()
# lr.fit(X_train, y_train)
# pred = model.predict(X_test)
# f1 = file('d:\\lr.pkl', 'wb')
# pickle.dump(lr, f1)
# f2 = file('d:\\y_test.pkl', 'wb')
# pickle.dump(y_test, f2)
# f3 = file('d:\\pred.pkl', 'wb')
# pickle.dump(pred, f3)

rng = np.random.RandomState(1)
regr = AdaBoostRegressor(DecisionTreeRegressor(
    max_depth=5), n_estimators=300, random_state=rng, loss='square')
start = time.clock()
code = '600568'
data = df[df['code'] == code]
data['target'] = data['close'].shift(1)
data = data[data['target'] > 0]
print 'code:%s,data size:%s' % (code, str(len(data)))
s = len(data) * split
X_train = data.ix[0:s, 'code':'turnover']
y_train = data.ix[0:s, 'target']
X_test = data.ix[s:, 'code':'turnover']
y_test = data.ix[s:, 'target']
print len(X_train), len(y_train), len(X_test), len(y_test)
regr.fit(X_train, y_train)
y_pred = regr.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
res = pd.DataFrame()
res['b'] = y_test[:]
res['a'] = y_pred
res.reindex()
print res
print regr.estimator_weights_
print regr.estimator_errors_
print 'error#mae:%s,mse:%s,r2:%s' % (str(mae), str(mse), str(r2))
print 'cost:%.03f s' % (time.clock() - start)

# for code in codes:
#     try:
#         t = datetime.now().time()
#         data = df[df['code'] == code]
#         data['target'] = data['close'].shift(1)
#         data = data[data['target'] > 0]
#         print 'code:%s,data size:%s' % (code, str(len(data)))
#         s = len(data) * split
#         X_train = data.ix[0:s, 'code':'turnover']
#         y_train = data.ix[0:s, 'target']
#         X_test = data.ix[s:, 'code':'turnover']
#         y_test = data.ix[s:, 'target']
#         print len(X_train), len(y_train), len(X_test), len(y_test)
#         regr.fit(X_train, y_train)
#         y_pred = regr.predict(X_test, y_test)
#         mae = mean_absolute_error(y_test, y_pred)
#         mse = mean_squared_error(y_test, y_pred)
#         r2 = r2_score(y_test, y_pred)
#         print 'error#mae:%s,mse:%s,r2:%s' % (str(mae), str(mse), str(r2))
#         print 'cost:%s' % str(datetime.now().time() - t)
#         if len(data) > 200:
#             break
#     except Exception, e:
#         pass
#         print e

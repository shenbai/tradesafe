# coding:utf-8

from org.tradesafe.data.history_data import HistoryData
from datetime import datetime, date, timedelta
import time
import os

from pandas.io import sql
from org.tradesafe.utils import utils
from org.tradesafe.data.index_code_conf import indices
from org.tradesafe.conf import config
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
start = time.clock()
code = '600446'
hd = HistoryData()
conn = db.get_history_data_db('D')
# df = None
# try:
#     df = pd.read_sql_query(
#         'select * from history_data where code=%s order by code, date([date]) asc' % code, conn)
#     print len(df)
# except Exception, e:
#     print e
df = hd.get_history_data_day()
codes = hd.get_all_stock_code()
# codes = [code]
lags = 1
# print len(df)
split = 0.9

rng = np.random.RandomState(1)
regr = AdaBoostRegressor(DecisionTreeRegressor(
    max_depth=5), n_estimators=300, random_state=rng, loss='square')
# start = time.clock()

# print regr.predict([)
for code in codes:
    try:
            if code == '600871':
                print code
            data = df[df['code'] == code]
            # data['target'] = data['p_change'].shift(1)
            data['target'] = data['close'].shift(1)
            data = data[data['target'] > -100]
            s = int(len(data) * split)
            print 'code:%s,data size:%s,split:%s' % (code, str(len(data)), str(s))
            X_train = data.ix[0:s, 'code':'turnover']
            y_train = data.ix[0:s, 'target']
            X_test = data.ix[s:, 'code':'turnover']
            y_test = data.ix[s:, 'target']
            print len(X_train), len(y_train), len(X_test), len(y_test)
            regr.fit(X_train, y_train)
            y_pred = regr.predict(X_test[:])
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            res = pd.DataFrame()
            res['today'] = X_test['close']
            res['real'] = y_test[:]
            res['predict'] = y_pred
            # res['diff'] = res['real']-res['predict']
            res['diff'] = res['predict']-res['today']
            res['real-diff'] = res['real'] - res['today']
            res['fp']=res['diff']*res['real-diff'] > 0
            # res.reindex()
#             print res
            print 'rate:%.04f' % (float(len(res[res['fp']==True]))/len(res))
            # print regr.estimator_weights_
            # print X_train.head(3)
            # print y_train.head(3)
             
            # print regr.estimator_errors_
            print 'error#mae:%s,mse:%s,r2:%s' % (str(mae), str(mse), str(r2))
            print 'cost:%.03f s' % (time.clock() - start)
            pickle.dump(regr, open('./%s.pkl' % code, 'wb'))
    except Exception, e:
        pass
        print e

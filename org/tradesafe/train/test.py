# coding:utf-8

import cPickle as pickle
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import AdaBoostRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.tree import DecisionTreeRegressor

from org.tradesafe.data.history_data import HistoryData
from org.tradesafe.db import sqlite_db as db
from org.tradesafe.conf import config

start = time.clock()
code = '600446'
enddate = '2016-07-13'
hd = HistoryData()
conn = db.get_history_data_db('D')
# df = None
# try:
#     df = pd.read_sql_query(
#         'select * from history_data where code=%s order by code, date([date]) asc' % code, conn)
#     print len(df)
# except Exception, e:
#     print e
df = hd.get_history_data_day(endDate=enddate)
codes = hd.get_all_stock_code()
# codes = [code]
lags = 1
# print len(df)
split = 0.9

rng = np.random.RandomState(1)
regr = AdaBoostRegressor(DecisionTreeRegressor(
    max_depth=5), n_estimators=300, random_state=rng, loss='square')
# start = time.clock()

mdic = {}
for code in codes:
    try:
        # if code == '600871':
        #     print code
        if code.startswith('30'):
            continue
        data = df[df['code'] == code]
        if len(data) < 400:
            continue
        # data['target'] = data['p_change'].shift(1)
        shift_1 = data['close'].shift(1)
        data['target'] = shift_1
        data = data[data['target'] > -1000]
        data.index = range(0, len(data))
        s = int(len(data) * split)
        X_train = data.ix[0:s, 'code':'turnover']
        y_train = data.ix[0:s, 'target']
        X_test = data.ix[s:, 'code':'turnover']
        y_test = data.ix[s:, 'target']
        # print 'code:%s,data size:%s,split:%s' % (code, str(len(data)), str(s))
        print code, len(X_train), len(y_train), len(X_test), len(y_test)
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
        res['diff'] = res['predict'] - res['today']
        res['real-diff'] = res['real'] - res['today']
        res['fp'] = res['diff'] * res['real-diff'] > 0

        # res.reindex()
        #             print res
        rate = (float(len(res[res['fp'] == True])) / len(res))
        print 'rate:%.04f' % (float(len(res[res['fp'] == True])) / len(res))
        # print regr.estimator_weights_
        # print X_train.head(3)
        # print y_train.head(3)

        # print regr.estimator_errors_
        print 'error#mae:%.03f,mse:%.04f,r2:%.04f' % (str(mae), str(mse), str(r2))
        print 'cost:%.03f s' % (time.clock() - start)
        pickle.dump(regr, open('%s/%s.pkl' % (config.model_dir, code), 'wb'))

        mdic[code] = (rate, mae, mse, r2)
    except Exception, e:
        pass
        print e

print mdic
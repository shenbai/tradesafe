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

start = time.clock()

mdic = {}
for code in codes:
    rng = np.random.RandomState(1)
    regr = AdaBoostRegressor(DecisionTreeRegressor(
        max_depth=5), n_estimators=1000, random_state=rng, loss='square')
    try:
        if code.startswith('30'):
            continue
        data = df[df['code'] == code].copy(deep=True)
        if len(data) < 400:
            continue
        shift_1 = data['p_change'].shift(1)
        # shift_1 = data['close'].shift(-1)
        data['target'] = shift_1
        data = data[data['target'] > -1000]
        data.index = range(0, len(data))
        s = int(len(data) * split)
        train = data.ix[0:s, :]
        test = data.ix[s:, :]
        print code, len(train), len(test)
        regr.fit(train.ix[:, 'code':'turnover'], train.ix[:, 'target'])
        y_pred = regr.predict(test.ix[:, 'code':'turnover'])
        mae = mean_absolute_error(test.ix[:, 'target'], y_pred)
        mse = mean_squared_error(test.ix[:, 'target'], y_pred)
        r2 = r2_score(test.ix[:, 'target'], y_pred)
        res = pd.DataFrame()
        res['date'] = test['date']
        res['close'] = test['p_change']
        res['target'] = test['target']
        res['predict'] = y_pred
        # res['diff'] = res['real']-res['predict']
        res['change'] = (res['target'] - res['close'])/res['close'] * 100
        res['pchange'] = (res['predict'] - res['close'])/res['close'] * 100
        res['fp'] = res['change'] * res['pchange'] > 0

        rate = (float(len(res[res['fp'] == True])) / len(res))
        print 'rate:%.04f' % rate
        # print regr.estimator_weights_
        # print X_train.head(3)
        # print y_train.head(3)
        # print regr.estimator_errors_
        print 'error#mae:%.03f,mse:%.04f,r2:%.04f' % (mae, mse, r2)
        print 'cost:%.03f s' % (time.clock() - start)
        pickle.dump(regr, open('%s/%s.pkl' % (config.model_dir, code), 'wb'))
        pUpData = res[res['pchange']>0]
        ptData = pUpData[pUpData['change']>0]
        # print upData
        print len(ptData), len(pUpData), len(ptData)/float(len(pUpData))
        mdic[code] = (rate, mae, mse, r2)
    except Exception, e:
        pass
        print e

print mdic
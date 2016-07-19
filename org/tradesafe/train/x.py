# coding:utf-8
import cPickle as pickle
from org.tradesafe.db import sqlite_db as db
from org.tradesafe.conf import config
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
from org.tradesafe.conf import config
from org.tradesafe.data.history_data import HistoryData




def backTest(trainEndDate, code, testDate, predictDate):
    conn = db.get_history_data_db('D')
    df = None
    # train more date
    # model = pickle.load(open('%s/%s.pkl' % (config.model_dir, code), 'r'))
    rng = np.random.RandomState(1)
    model = AdaBoostRegressor(DecisionTreeRegressor(
        max_depth=4), n_estimators=1000, random_state=rng, loss='square')
    df = pd.read_sql_query(
        "select * from history_data where date([date])<='%s' and code='%s' order by code, date([date]) asc" % (
            trainEndDate, code), conn)
    shift_1 = df['close'].shift(-2)
    df['target'] = shift_1
    data = df[df['target'] > -1000]

    X_train = data.ix[:, 'code':'turnover']
    y_train = data.ix[:, 'target']
    if len(X_train) < 500:
        return
    print len(X_train)
    # print data
    # for i in range(0, 10):
    #     model.fit(X_train, y_train)
    model.fit(X_train, y_train)
    # predict tomorrow
    try:
        df = pd.read_sql_query(config.sql_history_data_by_code_date % (code, testDate), conn)
        # print df
    except Exception, e:
        print e
    X_test = df.ix[:, 'code':'turnover']
    pred = model.predict(X_test)
    pdf = pd.read_sql_query(config.sql_history_data_by_code_date % (code, predictDate), conn)
    base = df['close'][0]
    pred = pred[0]
    targ = pdf['close'][0]
    change = (targ-base)/base * 100
    pchange = (pred-base)/base * 100

    print code, base, '%.03f' % pred, targ, '%.03f' % change, '%.03f' % pchange, pchange*change > 0

if __name__ == '__main__':
    # backTest('2016-07-13','000708', '2016-07-14', '2016-07-15')
    hd = HistoryData()
    codes = hd.get_all_stock_code()
    for code in codes:
        if code.startswith('30'):
            continue
        backTest('2016-07-13', code, '2016-07-14', '2016-07-15')

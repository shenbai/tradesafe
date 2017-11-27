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

r1 = 0.
r2 = 0.
good = []
for code in dic.keys():
    r,a,b,c = dic[code]
    # print(code, r, a,b,c)
    if r > 0.85:
        if code.startswith('3'):
            continue
        r1 = r1 + 1
        good.append(code)
        # print code
print r1
print r1 / len(dic.keys())
date = '2016-07-13'
conn = db.get_history_data_db('D')
date2 = '2016-07-14'
mypred = {}
total = 0.
trueNum = 0.
for code in good:
    df = None
    df2 = None
    t = False
    try:
        # print config.sql_history_data_by_code_date % (code, date)
        df = pd.read_sql_query(config.sql_history_data_by_code_date % (code, date), conn)
        # print len(df)
        df2 = pd.read_sql_query(config.sql_history_data_by_code_date % (code, date2), conn)
        if len(df) > 0 and len(df2) > 0:
            X_test = df.ix[:, 'code':'turnover']
            model = pickle.load(open('%s/%s.pkl' % (config.model_dir, code), 'r'))
            today = df['close'][0]
            nextday = df2['close'][0]
            predict = model.predict(X_test)[0]
            change = (nextday-today)/today * 100
            pchange = (predict-today)/today * 100
            diff = change - pchange
            t = (nextday-today) * (predict-today) > 0
            if t and pchange > 2:
                trueNum = trueNum + 1
            if pchange > 2:
                total = total + 1
                print code, today, nextday, predict, (nextday-today) * (predict-today) > 0, '%0.3f' % change, '%0.3f' % pchange, '%0.3f' % diff
            mypred[code] = (code, today, nextday, predict, (nextday-today) * (predict-today) > 0, nextday-predict, change, pchange, diff)
        # print mypred
    except Exception, e:
        print e
print trueNum/total
f = open('/home/tack/pred', 'w')
f.writelines(str(mypred))
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
code = '002113'
date = '2016-07-14'
conn = db.get_history_data_db('D')
df = None
# train more date
# model = pickle.load(open('%s/%s.pkl' % (config.model_dir, code), 'r'))

rng = np.random.RandomState(1)
model = AdaBoostRegressor(DecisionTreeRegressor(
    max_depth=4), n_estimators=1000, random_state=rng, loss='square')

df = pd.read_sql_query("select * from history_data where date([date])<='%s' and code='%s' order by code, date([date]) asc" % ('2016-07-12', code), conn)
shift_1 = df['close'].shift(-1)
df['target'] = shift_1
data = df[df['target'] > -1000]

X_train = data.ix[:, 'code':'turnover']
y_train = data.ix[:, 'target']
print len(X_train)
print data
# for i in range(0, 10):
#     model.fit(X_train, y_train)
model.fit(X_train, y_train)
# predict tomorrow
try:
    df = pd.read_sql_query(config.sql_history_data_by_code_date % (code, date), conn)
    print len(df)
    print df
except Exception, e:
    print e
X_test = df.ix[:, 'code':'turnover']
print model.predict(X_test)
print pd.read_sql_query(config.sql_history_data_by_code_date % (code, '2016-07-15'), conn)

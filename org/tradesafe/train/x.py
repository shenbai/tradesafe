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

code = '600520'
date = '2016-07-13'
conn = db.get_history_data_db('D')
df = None
try:
    df = pd.read_sql_query(config.sql_history_data_by_code_date % (code, date), conn)
    print len(df)
    print df
except Exception, e:
    print e
X_test = df.ix[:, 'code':'turnover']
model = pickle.load(open('./model.pkl', 'r'))
print model.predict(X_test)
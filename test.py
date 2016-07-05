import tushare as ts
from tushare.stock import cons as ct
import pandas as pd
import sqlite3 as lite
from pandas.io import sql
# today_all = ts.get_today_all()
# tick = ts.get_tick_data()
# today_all.to_csv('today_all.csv')
print ct.TICK_PRICE_URL % (ct.P_TYPE['http'], ct.DOMAINS['sf'], ct.PAGES['dl'],
                           'date', 'symbol')

data = [[1, 2, 3]]
head = ['a', 'b', 'c']
df = pd.DataFrame(data, columns=head)
print df
cnx = lite.connect('data.db')
sql_df = df.loc[:, :]
print sql_df
print type(sql_df)
# sql.write_frame(sql_df, name='all_index', con=cnx, if_exists='append')
sql.to_sql(sql_df, name='test', con=cnx, if_exists='append')

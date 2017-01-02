# coding: utf-8
data_dir = '/Users/tack/ts/data'
log_dir = '/Users/tack/ts/log'
history_D_data_db_file = data_dir + '/history_data_D.db'
history_W_data_db_file = data_dir + '/history_data_W.db'
history_M_data_db_file = data_dir + '/history_data_M.db'
history_5m_data_db_file = data_dir + '/history_data_5m.db'
history_15m_data_db_file = data_dir + '/history_data_15m.db'
history_30m_data_db_file = data_dir + '/history_data_30m.db'
history_60m_data_db_file = data_dir + '/history_data_60m.db'
history_tick_data_db_file = data_dir + '/history_data_tick.db'
money_flow_data_db_file = data_dir + '/money_flow.db'
tasks_db_file = data_dir + '/task.db'
dd_data_db_file = data_dir + '/dd_data.db'
memo_file = data_dir + '.memo'
model_dir = data_dir + '/models'
from org.tradesafe.utils import utils

utils.mkdirs(model_dir)
utils.mkdirs(log_dir)

IDX_ALL_INDEX_ = '''
CREATE UNIQUE INDEX IF NOT EXISTS [IDX_ALL_INDEX_] ON [all_index](
[date]  DESC,
[code]  DESC
)
'''


IDX_HISTORY_DATA_ = '''
CREATE UNIQUE INDEX IF NOT EXISTS [IDX_HISTORY_DATA_] ON [history_data](
[date]  DESC,
[code]  DESC
)
'''

TABLE_ALL_INDEX = '''
CREATE TABLE IF NOT EXISTS [all_index] (
CREATE TABLE [all_index] (
[date] TEXT  NULL,
[code] TEXT  NULL,
[open] REAL  NULL,
[close] REAL  NULL,
[low] REAL  NULL,
[heigh] REAL  NULL,
[chg] REAL NULL,
[chg_r] REAL NULL,
[vibration] REAL  NULL,
[vol] REAL  NULL,
[amount] REAL  NULL,
PRIMARY KEY ([date],[code])
)
'''

#日期	开盘	收盘	涨跌额	涨跌幅	最低	最高	成交量(手)	成交金额(万)	换手率
TABLE_HISTORY_DATA_DAY = '''
CREATE TABLE all_index (
  date text,
  code text,
  open real,
  close real,
  chg real,
  chg_r real,
  low real,
  heigh real,
  vibration real,
  volume real,
  amount real,
  PRIMARY KEY(date, code)
);
'''

TABLE_MONEY_FLOW = '''

'''

sql_last_date_index_all = 'select date from all_index order by date([date]) desc limit 1'
sql_last_date_history_data = 'select date from history_data order by date([date]) desc limit 1'
sql_last_date_history_data_by_code = 'select date from history_data where code="%s" order by date([date]) desc limit 1'
sql_last_date_history_data_qfq_by_code = 'select date from history_data_qfq where code="%s" order by date([date]) desc limit 1'
sql_last_date_dd_data = 'select date from dd_data order by date([date]) desc limit 1'
sql_history_data_by_code_date = "select * from history_data where code='%s' and date([date]) ='%s'"
sql_history_data_by_date_lt = "select * from history_data where date([date])<='%s' order by code, date([date]) asc"
sql_history_data_by_code_date_lt = "select * from history_data where code='%s' " \
                                   "and date([date])<='%s' order by date([date]) asc"
sql_history_data_all = 'select * from history_data order by code, date([date]) asc'
sql_history_data_by_code = 'select * from history_data where code="%s" order by date([date]) asc'
sql_history_data_by_code_date_between = "select * from history_data where code='%s' " \
                                   "and date([date])>='%s' and date([date])<='%s' order by date([date]) asc"

sql_history_data_qfq_by_code_date_between = "select * from history_data_qfq where code='%s' " \
                                        "and date([date])>='%s' and date([date])<='%s' order by date([date]) asc"

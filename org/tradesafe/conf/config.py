# coding: utf-8
data_dir = '/home/tack/data'
log_dir = '/home/tack/log'
history_D_data_db_file = data_dir + '/history_data_D.db'
history_W_data_db_file = data_dir + '/history_data_W.db'
history_M_data_db_file = data_dir + '/history_data_M.db'
history_5m_data_db_file = data_dir + '/history_data_5m.db'
history_15m_data_db_file = data_dir + '/history_data_15m.db'
history_30m_data_db_file = data_dir + '/history_data_30m.db'
history_60m_data_db_file = data_dir + '/history_data_60m.db'
history_tick_data_db_file = data_dir + '/history_data_tick.db'
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
TABLE_ALL_INDEX = '''
CREATE TABLE IF NOT EXISTS [all_index] (
CREATE TABLE [all_index] (
[date] TEXT  NULL,
[code] TEXT  NULL,
[open] REAL  NULL,
[close] REAL  NULL,
[change] REAL  NULL,
[pchange] TEXT  NULL,
[low] REAL  NULL,
[heigh] REAL  NULL,
[vibration] TEXT  NULL,
[volume] REAL  NULL,
[amount] REAL  NULL,
PRIMARY KEY ([date],[code])
)
'''
TABLE_HISTORY_DATA_DAY = '''
CREATE TABLE [history_data] (
[date] TEXT  NULL,
[code] TEXT  NULL,
[open] REAL  NULL,
[high] REAL  NULL,
[close] REAL  NULL,
[low] REAL  NULL,
[volume] REAL  NULL,
[price_change] REAL  NULL,
[p_change] REAL  NULL,
[ma5] REAL  NULL,
[ma10] REAL  NULL,
[ma20] REAL  NULL,
[v_ma5] REAL  NULL,
[v_ma10] REAL  NULL,
[v_ma20] REAL  NULL,
[turnover] REAL  NULL,
PRIMARY KEY ([date],[code])
)
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

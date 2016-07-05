# coding: utf-8
data_dir = '/home/tack/data'
history_day_data_db_file = data_dir + '/day_history.db'
history_tick_data_db_file = data_dir + '/tick_history.db'
tasks_db_file = data_dir + '/task.db'
memo_file = data_dir + '.memo'

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

sql_last_date_index_all = 'select date from all_index order by date([date]) desc limit 1'

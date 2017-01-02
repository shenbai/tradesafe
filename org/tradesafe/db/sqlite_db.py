# coding : utf-8

import org.tradesafe.conf.config as config
from org.tradesafe.utils import utils
from pandas.io import sql
import pandas as pd
import sqlite3

utils.mkdirs(config.data_dir)

def get_history_data_db(ktype='D'):
    if ktype == 'D':
        return sqlite3.connect(config.history_D_data_db_file)
    elif ktype == 'W':
        return sqlite3.connect(config.history_W_data_db_file)
    elif ktype == 'M':
        return sqlite3.connect(config.history_M_data_db_file)
    elif ktype == '5':
        return sqlite3.connect(config.history_5m_data_db_file)
    elif ktype == '15':
        return sqlite3.connect(config.history_15m_data_db_file)
    elif ktype == '30':
        return sqlite3.connect(config.history_30m_data_db_file)
    elif ktype == '60':
        return sqlite3.connect(config.history_60m_data_db_file)
    else:
        return sqlite3.connect(config.history_D_data_db_file)

def get_money_flow_db():
    return sqlite3.connect(config.money_flow_data_db_file)

def get_tick_history_db():
    utils.mkdirs(config.data_dir)
    return sqlite3.connect(config.history_tick_data_db_file)


def get_dd_data_db():
    utils.mkdirs(config.data_dir)
    return sqlite3.connect(config.dd_data_db_file)


def get_tasks_db():
    utils.mkdirs(config.data_dir)
    return sqlite3.connect(config.tasks_db_file)

if __name__ == '__main__':
    print config.sql_last_date_index_all
    # get_tasks_db().close()
    # get_history_data_db().close()
    # get_tick_history_db().close()
    con = get_history_data_db()
    # con.execute(config.TABLE_ALL_INDEX)
    # con.execute(config.IDX_ALL_INDEX_)
    # con.execute(config.IDX_HISTORY_DATA_)
    con.execute(config.TABLE_HISTORY_DATA_DAY)
    cur = con.execute(config.sql_last_date_index_all)
    print cur.fetchone()
    cur = con.execute('select count(*) from all_index')
    print cur.fetchone()[0]
    # df = pd.read_sql_query('select * from all_index', con)
    # print len(df.values)
    # print type(df.axes[0])

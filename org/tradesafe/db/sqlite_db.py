# coding : utf-8

import org.tradesafe.conf.config as config
from org.tradesafe.utils import utils
import sqlite3


def get_day_history_db():
    utils.mkdirs(config.data_dir)
    return sqlite3.connect(config.history_day_data_db_file)


def get_tick_history_db():
    utils.mkdirs(config.data_dir)
    return sqlite3.connect(config.history_tick_data_db_file)


def get_tasks_db():
    utils.mkdirs(config.data_dir)
    return sqlite3.connect(config.tasks_db_file)

if __name__ == '__main__':
    print config.history_day_data_db_file
    get_tasks_db().close()
    get_day_history_db().close()
    get_tick_history_db().close()

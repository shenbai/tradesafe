# coding:utf-8

from org.tradesafe.data.history_data import HistoryData
from org.tradesafe.db import sqlite_db as db

hd = HistoryData()
hd.download_history_data_day()
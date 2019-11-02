# coding: utf-8
'''
Created on 2016年6月19日

@author: tack
'''
import datetime
import logging
import os
from logging.handlers import RotatingFileHandler


def __getlog(name='mylog'):
    '''
        get a logging instance by name
    '''
    LOGGING_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
    DATE_FORMAT = '%y%m%d %H:%M:%S'
    formatter = logging.Formatter(LOGGING_FORMAT, DATE_FORMAT)
    # formatter = logging.Formatter('%(asctime)s:%(message)s')
    log = logging.getLogger(name)
    handler = RotatingFileHandler('logs/' + name + '.log', maxBytes=50 * 1024 * 1024, backupCount=10)
    # handler = logging.FileHandler('logs/' + name + '.log')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log


def __state_log(name='state'):
    '''
    create a logger instance
    :param name:
    :return:
    '''
    # LOGGING_FORMAT = '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s'
    log = logging.getLogger('.')
    handler = logging.FileHandler(name)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log

def read_last_state(name='state'):
    stat = {}
    if os.path.exists('state'):
        for line in open('state', 'r'):
            arr = line.strip().split(',')
            code = arr[0]
            # dt = arr[1].replace('-', '')
            dt = arr[1]
            if code in stat:
                if dt > stat[code]:
                    stat[code] = dt
            else:
                stat[code] = dt
    return stat


mylog = __getlog()
__state = read_last_state()
statelog = __state_log()


def get_laste_update_dt(code):
    return __state.get(code, None)

def mkdirs(path):
    '''
    make dirs
    '''
    if not os.path.exists(path):
        os.makedirs(path)


def today_last_year(years=1):
    lasty = datetime.datetime.today().date() + datetime.timedelta(-365 * years)
    return str(lasty)


def day_befor(days=1):
    lasty = datetime.datetime.today().date() - datetime.timedelta(days=days)
    return str(lasty)


if __name__ == '__main__':
    print(day_befor(10))

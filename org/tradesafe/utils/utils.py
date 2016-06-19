# coding: utf-8
'''
Created on 2016年6月19日

@author: tack
'''
import os
import datetime


def mkdirs(path):
    '''
    make dirs
    '''
    if not os.path.exists(path):
        os.makedirs(path)

def today_last_year(years=1):
    lasty = datetime.datetime.today().date() + datetime.timedelta(-365 * years)
    return str(lasty)
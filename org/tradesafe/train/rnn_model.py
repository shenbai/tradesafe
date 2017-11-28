# encoding:utf-8
from __future__ import print_function
import keras
from keras.models import Model, Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Input, Dense, TimeDistributed
from keras.layers import LSTM, GRU, Reshape, BatchNormalization
from keras import losses, metrics
import sys, os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataGenerator import DataGen
from keras.models import load_model
from keras.utils import CustomObjectScope
from keras.callbacks import ModelCheckpoint
from org.tradesafe.data.dataGenerator import DataGen
from org.tradesafe.data.history_data import HistoryData



def create_model(timestep=10, dim=100):
    model = Sequential()
    model.add(
        LSTM(
            256,
            input_dim=dim,
            input_length=timestep,
            return_sequences=True))
    model.add(TimeDistributed(Dense(128), input_shape=(timestep, 256)))
    # model.add(LSTM(64, return_sequences=True))
    model.add(LSTM(64))
    model.add(Dense(1))
    # model.add(Activation('linear'))
    model.add(Activation('relu'))
    model.compile(
        optimizer='rmsprop',
        loss=losses.mean_squared_error,
        metrics=[metrics.mae, metrics.mape, metrics.mse])
    return model

def train(model, data_generator):
    checkpointer = ModelCheckpoint(
        filepath='model.h5', verbose=1, save_best_only=True, save_weights_only=False)
    model.fit_generator(
        data_generator.next_train_batch(),
        steps_per_epoch=1000,
        epochs=10,
        callbacks=[checkpointer],
        validation_data=data_generator.next_val_batch(),
        validation_steps=100,
        workers=1)

def main():

    names = 'date,code,open,close,chg,chg_r,low,high,vibration,volume,amount,turnover'.split(
        ',')

    feats = names[:]
    feats.remove('date')
    feats.remove('code')
    hd = HistoryData()
    codes = hd.get_all_stock_code()
    dg = DataGen(codes, batch_size=64, time_step=15, pred_day=5, column_names=names)

    model = create_model(time_setp=dg.time_step, dim=dg.dim)
    print(model.summary())
    train(model, dg)
    

if __name__ == '__main__':
    main()
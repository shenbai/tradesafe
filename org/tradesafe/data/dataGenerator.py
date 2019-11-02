# encoding:utf-8

from numpy import array
# from sklearn.cross_validation import train_test_split
from sklearn.model_selection import train_test_split
from org.tradesafe.data.history_data import HistoryData
from org.tradesafe.utils.utils import mylog


class DataGen(object):
    '''
    trian data generator
    '''

    def __init__(self,
                 codes,
                 batch_size=64,
                 time_step=15,
                 pred_day=1,
                 column_names=None,
                 sort_by=['date'],
                 group_by=['code'],
                 label_column='high',
                 split_rate=0.05,
                 seed=7):
        '''
        :param codes:
        :param batch_size:
        :param time_step:
        :param pred_day:
        :param column_names:
        :param sort_by:
        :param group_by:
        :param split_rate:
        :param seed:
        '''

        self.codes = codes
        self.batch_size = batch_size
        self.time_step = time_step
        self.pred_day = pred_day
        self.column_names = column_names
        self.label_column = label_column

        self.train_codes, self.val_codes = train_test_split(
            array(self.codes), random_state=seed, test_size=split_rate)

        feats = self.column_names[:]
        for n in set(sort_by + group_by):
            feats.remove(n)

        self.feats = feats
        self.dim = len(self.feats)

        self.hd = HistoryData()
        mylog.info('loading all data')
        # df = self.hd.get_history_data_all()
        # df = df.sort_values(by=sort_by)
        # dfg = df.groupby(by=group_by)
        # self.all_data = dfg
        mylog.info('data load complete')

    def set_data(self, data_df):
        mylog.info('set data')
        self.all_data = data_df

    def next_val_batch(self):
        '''
        :return: batch examples of validate dataset
        '''
        while 1:
            for k, g in self.all_data:
                if k in self.val_codes:
                    if g is not None and not g.empty:
                        if len(
                                g
                        ) < self.time_step + self.batch_size + self.pred_day:
                            continue
                        i = 0
                        batch_X = []
                        batch_y = []
                        ALL_X = g[self.feats].as_matrix().astype(float)
                        ALL_y = g[[self.label_column
                                   ]].as_matrix().astype(float)
                        All_close = g[['close']].as_matrix().astype(float)
                        batch_y_ = []

                        while i < len(g) - self.pred_day - max(
                                self.time_step, self.batch_size):

                            X = ALL_X[i:i + self.time_step]
                            y = ALL_y[i + self.time_step:
                                      i + self.time_step + self.pred_day]
                            y_today = All_close[i + self.time_step - 1]
                            batch_X.append(X)
                            batch_y.append(y.max())
                            batch_y_.append(y.max())
                            i += 1
                            if len(batch_y) == self.batch_size:
                                yield array(batch_X), array(batch_y).reshape(
                                    self.batch_size, 1)
                                batch_X = []
                                batch_y = []

    def next_train_batch(self):
        '''
        :return: batch examples
        '''
        while 1:
            for k, g in self.all_data:
                if k in self.train_codes:
                    if g is not None and not g.empty:
                        if len(
                                g
                        ) < self.time_step + self.batch_size + self.pred_day:
                            continue
                        i = 0
                        batch_X = []
                        batch_y = []
                        ALL_X = g[self.feats].as_matrix().astype(float)
                        ALL_y = g[[self.label_column
                                   ]].as_matrix().astype(float)
                        
                        All_close = g[['close']].as_matrix().astype(float)

                        while i < len(g) - self.pred_day - max(
                                self.time_step, self.batch_size):

                            X = ALL_X[i:i + self.time_step]
                            y = ALL_y[i + self.time_step:
                                      i + self.time_step + self.pred_day]
                            y_today = All_close[i + self.time_step - 1]
                            batch_X.append(X)
                            batch_y.append(y.max())
                            i += 1
                            if len(batch_y) == self.batch_size:
                                yield array(batch_X), array(batch_y).reshape(
                                    self.batch_size, 1)
                                batch_X = []
                                batch_y = []


    def next_predict_example(self):
        '''
        :return: batch examples
        '''
        for k, g in self.all_data:
            if g is not None and not g.empty:
                if len(g) < self.time_step:
                    continue
                batch_X = []
                ALL_X = g[self.feats].as_matrix().astype(float)
                dt = g.date.iloc[-1]
                X = ALL_X[0-self.time_step:]
                batch_X.append(X)
                yield dt, k, array(batch_X)
                batch_X = []

if __name__ == '__main__':
    names = 'date,code,open,close,chg,chg_r,low,high,vibration,volume,amount,turnover'.split(
        ',')

    feats = names[:]
    feats.remove('date')
    feats.remove('code')
    hd = HistoryData()
    codes = hd.get_all_stock_code()
    dg = DataGen(codes, 64, 15, 5, names)

    for x, y in dg.next_val_batch():
        print(x.shape)
        print(y.shape)
        print(x)
        print(y)
        break

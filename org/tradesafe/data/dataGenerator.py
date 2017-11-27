# encoding:utf-8

from numpy import array
# from sklearn.cross_validation import train_test_split
from sklearn.model_selection import train_test_split
from org.tradesafe.data.history_data import HistoryData


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

    def next_val_batch(self):
        '''
        :return: batch examples of validate dataset
        '''
        while 1:
            for val_code in self.val_codes:
                df = self.hd.get_history_data(code=val_code)
                if df is not None and not df.empty:
                    if len(
                            df
                    ) < self.time_step + self.batch_size + self.pred_day:
                        continue
                    i = 0
                    batch_X = []
                    batch_y = []
                    ALL_X = df[self.feats].as_matrix().astype(float)
                    ALL_y = df[[self.label_column]].as_matrix().astype(float)

                    while i < len(df) - self.pred_day - max(
                            self.time_step, self.batch_size):

                        X = ALL_X[i:i + self.time_step]
                        y = ALL_y[i + self.time_step:
                                  i + self.time_step + self.pred_day]

                        batch_X.append(X)
                        batch_y.append(y.max())
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
            for train_code in self.train_codes:
                df = self.hd.get_history_data(code=train_code)
                if df is not None and not df.empty:
                    if len(
                            df
                    ) < self.time_step + self.batch_size + self.pred_day:
                        continue
                    i = 0
                    batch_X = []
                    batch_y = []
                    ALL_X = df[self.feats].as_matrix().astype(float)
                    ALL_y = df[[self.label_column]].as_matrix().astype(float)

                    while i < len(df) - self.pred_day - max(
                            self.time_step, self.batch_size):

                        X = ALL_X[i:i + self.time_step]
                        y = ALL_y[i + self.time_step:
                                  i + self.time_step + self.pred_day]

                        batch_X.append(X)
                        batch_y.append(y.max())
                        i += 1
                        if len(batch_y) == self.batch_size:
                            yield array(batch_X), array(batch_y).reshape(
                                self.batch_size, 1)
                            batch_X = []
                            batch_y = []


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

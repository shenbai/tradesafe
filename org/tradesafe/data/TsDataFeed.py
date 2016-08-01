# coding:utf-8

import datetime
import backtrader.feed as feed
from backtrader import date2num

class PandasDirectDataX(feed.DataBase):
    '''
    Uses a Pandas DataFrame as the feed source, iterating directly over the
    tuples returned by "itertuples".

    This means that all parameters related to lines must have numeric
    values as indices into the tuples

    Note:

      - The ``dataname`` parameter is a Pandas DataFrame

      - A negative value in any of the parameters for the Data lines
        indicates it's not present in the DataFrame
        it is
    '''

    params = (
        ('datetime', 1),
        ('open', 3),
        ('high', 4),
        ('low', 6),
        ('close', 5),
        ('volume', 7),
        ('openinterest', -1),
    )

    datafields = [
        'datetime', 'open', 'high', 'low', 'close', 'volume', 'openinterest'
    ]

    def start(self):
        super(PandasDirectDataX, self).start()

        # reset the iterator on each start
        self._rows = self.p.dataname.itertuples()

    def _load(self):
        try:
            row = next(self._rows)
        except StopIteration:
            return False

        # Set the standard datafields - except for datetime
        for datafield in self.datafields[1:]:
            # get the column index
            colidx = getattr(self.params, datafield)

            if colidx < 0:
                # column not present -- skip
                continue
            # get the line to be set
            line = getattr(self.lines, datafield)

            # indexing for pandas: 1st is colum, then row
            line[0] = row[colidx]

        # datetime
        colidx = getattr(self.params, self.datafields[0])
        tstamp = row[colidx]
        # print tstamp
        # convert to float via datetime and store it
        tstamp = datetime.datetime.strptime(tstamp, '%Y-%m-%d')
        # dt = tstamp.to_datetime()
        dt = tstamp
        # print dt
        dtnum = date2num(dt)
        # print dtnum
        # get the line to be set
        line = getattr(self.lines, self.datafields[0])
        line[0] = dtnum

        # Done ... return
        return True

if __name__ == '__main__':
    import backtrader as bt
    from org.tradesafe.db import sqlite_db as db
    from org.tradesafe.conf import config
    import pandas as pd
    conn = db.get_history_data_db('D')
    df = pd.read_sql_query(
        "select * from history_data where code='%s' order by date([date]) asc" % '600022', conn)
    data = PandasDirectDataX(dataname=df)
    print type(data)
    print dir(data)
# -*- coding: utf-8 -*-
"""
-----------------------------------------------
# File: hour_level_demo.py
# This file is created by Chuanting Zhang
# Email: chuanting.zhang@kaust.edu.sa
# Date: 2019-11-21 (YYYY-MM-DD)
-----------------------------------------------
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join

import h5py

height, width = 100, 100


def load_data(nov, dec):
    data = []
    idx = []
    for path in [nov, dec]:
        for f in listdir(path):
            if isfile(join(path, f)):
                print(f)
                df_today = pd.read_csv(path+f, header=None, sep='\t',
                                       names=['id', 'time', 'country',
                                              'sms-in', 'sms-out', 'call-in',
                                              'call-out', 'internet'])
                df_today = df_today.fillna(0)
                utc_to_rome = 3600000
                df_today['date'] = pd.to_datetime(df_today['time'] + utc_to_rome, unit='ms', utc=True)

                df_grouped = df_today.groupby(['id', 'date']).sum().reset_index()
                # print df_grouped.head(10)
                # print df_grouped.tail(10)

                times = pd.DatetimeIndex(df_grouped.date)
                year, month, day = times.year[0], times.month[0], times.day[0]
                df_grouped_time = df_grouped.groupby([times.hour, 'id']).sum().reset_index()

                intervals = np.unique(df_grouped_time.date.values)
                cell_ids = set(range(1, height*width+1))

                for hour in intervals:
                    idx.append(np.string_(pd.datetime(year, month, day, hour)))
                    tmp_data = df_grouped_time[df_grouped_time['date']==hour]
                    id = set(tmp_data['id'])
                    tmp_data.index = id
                    diff = cell_ids - set(tmp_data.index.values)

                    for cell in diff:
                        n = 0
                        if (cell - width) in tmp_data.index:
                            a = tmp_data.loc[cell-width]
                            n += 1

                        if (cell - 1) in tmp_data.index:
                            b = tmp_data.loc[cell-1]
                            n += 1

                        if (cell + 1) in tmp_data.index:
                            c = tmp_data.loc[cell+1]
                            n += 1

                        if (cell + width) in tmp_data.index:
                            d = tmp_data.loc[cell+width]
                            n += 1

                        if n > 0:
                            # print((a+b+c+d)/n)
                            tmp_data.loc[cell] = (a+b+c+d) / n
                        else:
                            print('ct')
                            tmp_data.loc[cell] = 0

                    tmp_data.sort_index(axis=0, inplace=True) # make sure the inserted record is right
                    result = tmp_data[['sms-in', 'sms-out', 'call-in', 'call-out', 'internet']].values
                    # print result.shape
                    data.append(result)

    return idx, data


def main():
    path_nov = 'D:/Dataset/Milano/Telecommunications/Nov/full/'
    path_dec = 'D:/Dataset/Milano/Telecommunications/Nov/full/'

    f = h5py.File('d:/all_data_ct.h5', 'w')
    idx, data = load_data(path_nov, path_dec)
    f.create_dataset(name='idx', data=idx)
    f.create_dataset(name='data', data=data)
    f.close()


if __name__ == '__main__':
    main()
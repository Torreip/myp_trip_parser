#!/usr/bin/env python3

import logging
import os
import sys
import re
import pandas as pd
import numpy as np

from matplotlib import pyplot as plt

logger = logging.getLogger(__name__)


class Parser():
    log = logger
    data = None

    def __init__(self, in_file: str, with_location: bool = False):
        self.file = os.path.normpath(in_file)
        self.__with_location = with_location
        self.__open()
        self.__fix_values()

        print(self.data.info())
        # print(self.data.describe())
        print(self.data.head())

    def __open(self):
        self.data = pd.read_csv(
            self.file, sep=';', decimal=",", parse_dates=["date", ], encoding='utf-8')

        # column names depends on the language, by mapping them here, we can stay general afterwards
        self.data = self.data.rename(columns={
            "date": "date",
            "heure de départ": "start_h",
            "heure d'arrivée": "end_h",
            "durée": "duration",
            "adresse de départ": "start_addr",
            "adresse d'arrivée": "end_addr",
            "distance": "dist",
            "Kilométrage au compteur (km)": "km_odo",
            "consomation moy (l/100km)": "cons",
            "prix du carburant (EUR/l)": "carb_price",
            "cout (EUR)": "cost",
            "catégorie": "category",
        })

        # 'heure de départ', 'heure d'arrivée' and 'durée' are in hh:mm
        for col in ['start_h', 'end_h']:
            self.data[col] = pd.to_datetime(self.data[col],
                                            format="%H:%M", errors='raise').dt.time

        # add :00 to convert to timedelta
        self.data['duration'] += ':00'
        self.data['duration'] = pd.to_timedelta(self.data['duration'])

        # drop Unnamed fields
        attr_l = self.data.columns
        drop_attr_l = [a for a in attr_l if re.match(
            '.*Unnamed.*', a) is not None]
        self.data.drop(columns=drop_attr_l, inplace=True)

        # drop location
        if not self.__with_location:
            self.data.drop(columns=[
                'start_addr',
                'end_addr',
            ], inplace=True)

        # drop un-necessary fields
        self.data.drop(columns=[
            'category'
        ], inplace=True)

        # drop km counter, as it is the sum of km, so duplicate info
        self.data.drop(columns=[
            'km_odo',
        ], inplace=True)

    def __fix_values(self):
        '''
        fixes specific to my data set:
        I filled in 1405 eur/L instead of 1.405
        I filled in 133 eur/L instead of 1.33
        need to fix 2 fields:
        - carb_price
        - cost

        I forgot to set the year at the very beginning, so the first samples have a wrong date
        2007-03-01 has to be switched for 2017-10-15
        '''
        value_cols = ['carb_price', 'cost']
        self.data[value_cols] = self.data[value_cols].mask(
            self.data['carb_price'] == 1405, self.data[value_cols]/1000)

        value_cols = ['carb_price', 'cost']
        self.data[value_cols] = self.data[value_cols].mask(
            self.data['carb_price'] == 133, self.data[value_cols]/100)

        # Fix date of first samples
        value_cols = ['date']
        self.data[value_cols] = self.data[value_cols].mask(
            self.data['date'] == np.datetime64('2007-03-01'), np.datetime64('2017-10-15'))

    def hist(self):
        '''
        pandas dataframe hist, shows the sample repartition, not super useful, except for checking for outliers/errors
        '''
        _ = self.data.hist(figsize=(20, 14))
        plt.show()

    def get_dataframe(self):
        return self.data


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('matplotlib.font_manager').setLevel(
        level=logging.WARNING)
    in_file = "test.csv"

    p = Parser(in_file, with_location=True)
    # p.hist()


if __name__ == "__main__":
    main()

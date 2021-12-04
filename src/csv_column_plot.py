import csv

from datetime import datetime

from . import date_utils
from .plot import Plot


class CsvColumnPlot(Plot):

    def __init__(self, path, column, label=None, should_skip_first_line=False, start_date=datetime(2020, 3, 1)):

        if label:
            self._label = label
        else:
            self._label = column

        reader = csv.reader(open(path, encoding='utf-8'))

        if should_skip_first_line:
            next(reader)

        titles = next(reader)

        # Normalize 90+ and 90-99
        if column not in titles and column.replace('90+', '90-99') in titles:
            column = column.replace('90+', '90-99')

        column_index = titles.index(column)

        self.dates = []
        self.values = []

        for row in reader:
            # Skip old dates
            date = date_utils.str_to_datetime(row[0])
            if date < start_date:
                continue

            # Record date
            self.dates.append(date_utils.datetime_to_num(date))

            # Record value
            str_value = row[column_index]
            self.values.append(0 if str_value == '' else float(str_value))

    def x(self):
        return self.dates

    def y(self):
        return self.values

    def label(self):
        return self._label

    def separate_y_axis(self):
        return False

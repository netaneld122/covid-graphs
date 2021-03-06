import numpy
import math
import itertools

from . import date_utils
from .plot import Plot


class Modifier(Plot):
    def __init__(self, plot):
        self.plot = plot

    def x(self):
        return self.plot.x()

    def y(self):
        return self.plot.y()

    def label(self):
        return self.plot.label()

    def separate_y_axis(self):
        return self.plot.separate_y_axis()


class Multiply(Modifier):
    def __init__(self, factor, plot):
        super().__init__(plot)
        self._y = [v * factor for v in self.plot.y()]

    def y(self):
        return self._y


class Pow(Modifier):
    def __init__(self, exp, plot):
        super().__init__(plot)
        self._y = [v ** exp for v in self.plot.y()]

    def y(self):
        return self._y


class Cumulate(Modifier):
    def __init__(self, plot):
        super().__init__(plot)
        self._y = [sum(self.plot.y()[:i]) for i, v in enumerate(self.plot.y())]

    def y(self):
        return self._y


class Average(Modifier):
    def __init__(self, window, plot):
        super().__init__(plot)
        self._x = plot.x()[window-1:]
        self._y = self.moving_average(plot.y(), window)

    @staticmethod
    def moving_average(x, w):
        return numpy.convolve(x, numpy.ones(w), 'valid') / w

    def x(self):
        return self._x

    def y(self):
        return self._y


class ChopFromEnd(Modifier):
    def __init__(self, chop, plot):
        super().__init__(plot)
        self._x = plot.x()[:-chop]
        self._y = plot.y()[:-chop]

    def x(self):
        return self._x

    def y(self):
        return self._y


class OnlyFromDate(Modifier):
    def __init__(self, date, plot):
        super().__init__(plot)

        chop = 0
        for chop, x in enumerate(plot.x()):
            if date <= date_utils.num_to_datetime(x):
                break

        self._x = plot.x()[chop:]
        self._y = plot.y()[chop:]

    def x(self):
        return self._x

    def y(self):
        return self._y


class Group(Modifier):
    def __init__(self, label, plots):
        super().__init__(plots[0])
        zipped = itertools.zip_longest(*(plot.y() for plot in plots))
        self._y = [sum(zip) for zip in zipped]
        self._label = label

    def y(self):
        return self._y

    def label(self):
        return self._label


class DeriveToDays(Modifier):
    def __init__(self, plot):
        super().__init__(plot)

        self._x = []
        self._y = []

        delta = 0
        prev_x = plot.x()[0]
        for i, x in enumerate(plot.x()):
            if i == 0:
                continue
            d = plot.y()[i] - plot.y()[i-1]
            if date_utils.is_same_day(prev_x, x):
                delta += d
            else:
                self._x.append(prev_x)
                self._y.append(delta + d)
                delta = 0
            prev_x = x

    def x(self):
        return self._x

    def y(self):
        return self._y


class SeparateYAxis(Modifier):
    def __init__(self, plot):
        super().__init__(plot)

    def separate_y_axis(self):
        return True


class AdjustForTests(Modifier):
    def __init__(self, plot, tests):
        super().__init__(plot)
        self._y = [y * self.inverse(tests.y()[i+1]) for i, y in enumerate(plot.y())]

    @staticmethod
    def inverse(value):
        return math.sqrt(100000 / value)

    def y(self):
        return self._y


class Percentage(Modifier):
    def __init__(self, nominator_plot, denominator_plot, label=None):
        super().__init__(nominator_plot)
        self._y = [y * 100 / denominator_plot.y()[i] for i, y in enumerate(nominator_plot.y())]
        self._label = label

    def y(self):
        return self._y

    def label(self):
        if self._label:
            return self._label
        return super().label()


class QuantifyLabel(Modifier):
    def __init__(self, suffix_format, plot):
        super().__init__(plot)
        self.suffix_format = suffix_format

    def label(self):
        return self.plot.label() + ' ' + self.suffix_format.format(self.y()[-1])


class ToRatio(Modifier):
    def __init__(self, plot):
        super().__init__(plot)

        self._y = []
        for i, y in enumerate(plot.y()):
            if i == 0:
                continue
            self._y.append(y / plot.y()[i-1])

    def y(self):
        return self._y

    def x(self):
        return self.plot.x()[1:]

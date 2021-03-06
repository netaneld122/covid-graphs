import csv
import itertools
from datetime import datetime, timedelta
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


AGES = 60  # +
SPLIT = AGES // 10 + 1


def str_to_datetime(s):
    iso_datetime = s.replace('T', ' ').split('.')[0]
    return datetime.fromisoformat(iso_datetime)


def row_to_values(row, aggregate):
    if aggregate:
        values = [sum(map(int, row[2:SPLIT]))] + [sum(map(int, row[SPLIT:11]))]
    else:
        values = row[1:SPLIT] + [sum(map(int, row[SPLIT:11]))]
    return [int(v) for v in values]


def population_factors(aggregate):
    population = [
        1937676,  # 0-9
        1505185,  # 10-19
        1277634,  # 20-29
        1186386,  # 30-39
        1080768,  # 40-49
        832687,   # 50-59
        735380,   # 60-69
        462148,   # 70-79
        222547,   # 80-89
        50589,    # 90+
    ]

    population = population[1 if aggregate else 0:SPLIT-1] + [sum(population[SPLIT-1:])]
    # return [10**7 / p for p in population]
    return [100 / p for p in population]


def second_wave_factors():
    return [
        0.46,  # 0-9
        0.22,  # 10-19
        0.25,  # 20-29
        0.34,  # 30-39
        0.38,  # 40-49
        0.49,  # 50-59
        0.39,   # 0.70,  # 60-69
        1.4,   # 70-79
        1.7,   # 80+
    ]


def no_factors():
    return [1] * 10


def is_same_day(date1, date2):
    return date1.strftime('%Y%m%d') == date2.strftime('%Y%m%d')


def read_ages(start_date, factors, aggregate):
    reader = csv.reader(open('ages_dists.csv'))
    next(reader)  # Skip gender titles
    if aggregate:
        next(reader)  # Skip titles
        titles = [f'10-{SPLIT * 10 - 11}'] + [f'{SPLIT * 10 - 10}+']
    else:
        titles = next(reader)[1:SPLIT] + [f'{SPLIT - 1}0+']
    dates = []
    value_lists = [[] for _ in range(len(titles))]

    # Aggregate
    prev_values = None
    prev_date = None
    for row in reader:
        date = str_to_datetime(row[0])
        if date < start_date:
            prev_values = [v for v in row_to_values(row, aggregate)]
            prev_date = date
            continue

        if is_same_day(prev_date, date):
            # This is an update within the same-day - add to the previous value
            for i, value in enumerate(row_to_values(row, aggregate)):
                value_lists[i][-1] += (value - prev_values[i]) * factors[i]
        else:
            # This is a new day update
            dates.append(mdates.date2num(date))

            for i, value in enumerate(row_to_values(row, aggregate)):
                value_lists[i].append((value - prev_values[i]) * factors[i])

        prev_values = [v for v in row_to_values(row, aggregate)]
        prev_date = date

    return dates, titles, value_lists


def moving_average(x, w):
    return numpy.convolve(x, numpy.ones(w), 'valid') / w


def averager(value_lists, w):
    for value_list in value_lists:
        yield list(moving_average(value_list, w))


def vertical_span(plt, date, date_end, color):
    plt.axvspan(date, date_end, facecolor=color, alpha=0.5)
    plt.text(date, 150, '', rotation=90)


def vertical_line(plt, date, text, color):
    plt.axvline(x=date, color=color, alpha=0.5)
    bottom, top = plt.ylim()
    plt.text(date, bottom + top / 50, text, rotation=90)


def draw_events(plt, start_date):
    vacc1_date = datetime(2021, 1, 1)
    vertical_line(plt, vacc1_date, 'Vaccine #1 (1 million)', 'g')
    vertical_line(plt, vacc1_date + timedelta(days=21), 'Vaccine #2', 'g')
    vertical_line(plt, vacc1_date + timedelta(days=28), 'Vaccine #2+week', 'g')

    partial_lockdown = '#f0cccc'
    full_lockdown = '#f08888'

    # Second lockdown
    if start_date < datetime(2020, 9, 18):
        vertical_span(plt, datetime(2020, 9, 18), datetime(2020, 9, 25), partial_lockdown)
        vertical_span(plt, datetime(2020, 9, 25), datetime(2020, 10, 13), full_lockdown)
        vertical_span(plt, datetime(2020, 10, 13), datetime(2020, 10, 17), partial_lockdown)

    # Third lockdown
    vertical_span(plt, datetime(2020, 12, 27), datetime(2021, 1, 8), partial_lockdown)
    vertical_span(plt, datetime(2021, 1, 8), datetime(2021, 2, 4), full_lockdown)


def normalize_values_to_be_relative(value_lists):
    zipped = itertools.zip_longest(*value_lists)
    summed = [sum(v) for v in zipped]
    for value_list in value_lists:
        for i, v in enumerate(value_list):
            value_list[i] = value_list[i] / summed[i]


def fill_vaccine_effect(ax, dates, value_lists):
    vaccine_effect_date = datetime(2021, 1, 20)
    for i, date in enumerate(dates):
        if is_same_day(mdates.num2date(date), vaccine_effect_date):
            break
    ax.fill_between(dates[i:], value_lists[0][i:], value_lists[1][i:])


def main():

    # start_date = datetime(2020, 6, 20)
    start_date = datetime(2020, 8, 10)
    # start_date = datetime(2020, 12, 20)

    dates, titles, value_lists = read_ages(
        start_date=start_date,
        factors=[1, 6.7],
        # factors=second_wave_factors(),
        # factors=population_factors(False),
        # factors=no_factors(),
        aggregate=True
    )

    value_lists = [v[:-1] for v in value_lists]
    dates = dates[:-1]

    # Averaging
    avg_window = 7
    dates = dates[avg_window-1:]
    value_lists = list(averager(value_lists, avg_window))

    fig, ax = plt.subplots(figsize=(23, 10))

    for i, value_list in enumerate(value_lists):
        alpha = 0.8
        ax.scatter(dates, value_list, label=titles[i], alpha=alpha)
        line, = ax.plot(dates, value_list, 'o--', alpha=alpha)
        ax.text(
            dates[-1] + 1,
            value_list[-1] if i != 0 else value_list[-1],
            titles[i],
            fontsize=11,
            color=line.get_color())

    fill_vaccine_effect(ax, dates, value_lists)

    # normalize_values_to_be_relative(value_lists)
    # ax.stackplot(dates, value_lists, labels=titles)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 30)))

    ax.set_ylabel(f'{avg_window}-day rolling avg % of daily confirmed')

    ax.legend(loc='upper left')
    ax.grid(True)

    fig.autofmt_xdate()

    draw_events(plt, start_date)

    plt.show()


if __name__ == '__main__':
    # plt.xkcd()
    main()

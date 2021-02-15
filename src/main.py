from datetime import datetime

from .csv_column_plot import CsvColumnPlot
from .modifiers import Multiply, Average, OnlyFromDate, Group, DeriveToDays, SeparateYAxis, QuantifyLabel
from .plot_viewer import PlotViewer
from .plot_utils import normalize_plots_to_date


def expand_age_group(age_group):
    if age_group == '90+':
        return '90+'

    all_age_groups = (f'{r}-{r+9}' for r in range(0, 90, 10))
    all_age_groups = list(all_age_groups) + ['90+']

    index = int(age_group.split('+')[0]) // 10
    return all_age_groups[index:]


def create_age_plots(ages):
    age_plots = []
    for age_group in ages:
        if '+' in age_group:
            # Group several age groups together
            grouped_plots = []
            for expanded_age_group in expand_age_group(age_group):
                grouped_plots.append(CsvColumnPlot(
                    path='ages_dists.csv',
                    should_skip_first_line=True,
                    column=expanded_age_group))
            age_plots.append(DeriveToDays(Group(label=age_group, plots=grouped_plots)))
        else:
            # Add individual age group
            age_plots.append(DeriveToDays(CsvColumnPlot(
                path='ages_dists.csv',
                should_skip_first_line=True,
                column=age_group)))
    return age_plots


def post_process_age_plots(ages, age_plots, should_group, should_normalize, multiply):
    # Group lower ages
    if should_group:
        lowest_age = ages[0].split("-")[0]
        highest_age = ages[-2].split("-")[1]
        age_plots = (
            Group(label=f'{lowest_age}-{highest_age}', plots=(age_plots[:-1])),
            age_plots[-1])

    # Normalize peak
    if should_normalize:
        age_plots = normalize_plots_to_date(datetime(2021, 1, 13), age_plots)

    age_plots = [Average(7, Multiply(multiply, plot)) for plot in age_plots]

    return age_plots


def main():
    viewer = PlotViewer()

    # Vaccinated
    viewer.add_plot(QuantifyLabel('({}%)', SeparateYAxis(CsvColumnPlot(
            path='vaccinated.csv',
            column='Vaccinated population percentage',
            label='Dose #1'))))

    viewer.add_plot(QuantifyLabel('({}%)', SeparateYAxis(CsvColumnPlot(
            path='vaccinated.csv',
            column='Second dose population precentage',
            label='Dose #2'))))

    # Severe Cases
    viewer.add_plot(QuantifyLabel('({:0.0f})', CsvColumnPlot(
            path='hospitalized_and_infected.csv',
            column='Hard',
            label='Severe')))

    # Hospitalized
    viewer.add_plot(QuantifyLabel('({:0.0f})', CsvColumnPlot(
            path='hospitalized_and_infected.csv',
            column='Hospitalized')))

    # Tests
    viewer.add_plot(Multiply(0.03, QuantifyLabel('({:0.0f})', Average(7, CsvColumnPlot(
        path='hospitalized_and_infected.csv',
        column='Tests for idenitifaction',
        label='Tests')))))

    # Age groups
    ages = ('10-19', '20-29', '30-39', '40-49', '50-59', '60+')
    age_plots = create_age_plots(ages)
    age_plots = post_process_age_plots(ages, age_plots,
                                       should_group=True,
                                       should_normalize=True,
                                       multiply=0.3)
    viewer.add_plots(age_plots)

    # Apply global modifiers
    viewer.plots = [
        OnlyFromDate(datetime(2020, 12, 10), plot) for plot in viewer.plots
    ]

    viewer.show()


def get_population():
    return {
        '0-9':   1937676,
        '10-19': 1505185,
        '20-29': 1277634,
        '30-39': 1186386,
        '40-49': 1080768,
        '50-59': 832687,
        '60-69': 735380,
        '70-79': 462148,
        '80-89': 222547,
        '90+':   50589,
    }


def vaccinated():
    viewer = PlotViewer()

    population = get_population()

    for age_group in expand_age_group('10+'):
        viewer.add_plot(
            QuantifyLabel('({:0.2f}%)', Average(7, DeriveToDays(Multiply(100 / population[age_group], CsvColumnPlot(
                path='vaccinated_by_age.csv',
                column=f'{age_group} first dose',
                label=age_group))))))

    viewer.add_plot(QuantifyLabel('({:0.2f}%)', Average(7, Multiply(100 / sum(population.values()), CsvColumnPlot(
            path='vaccinated.csv',
            column='Vaccinated (daily)',
            label='Average')))))

    viewer.show(False)


if __name__ == '__main__':
    # main()
    vaccinated()

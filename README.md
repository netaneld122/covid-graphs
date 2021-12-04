# israel_moh_covid_dashboard_data
Data pulled from the Israeli Minsitry of Health's COVID-19 dashboard's API.


### How to generate a graph
* Install `python3`
* Execute `python -m src.main` from the repository root

Example:

![Example](graph.png)

### Data Source

The dashboard can be found at:
* https://datadashboard.health.gov.il/COVID-19/general

The data is fetched by sending a request to the address: 
* https://datadashboardapi.health.gov.il/api/queries/_batch

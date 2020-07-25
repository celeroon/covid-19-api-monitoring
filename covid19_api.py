import requests
import sqlite3
from plotly.graph_objs import Bar
from plotly import offline

#Make an API call, and store the response.
url = 'https://api.covid19api.com/summary'
headers = {'Accept': 'application/json'}
r = requests.get(url, headers=headers)
print(f"Status code: {r.status_code}")

conn = sqlite3.connect('covid19.db')
c = conn.cursor()

with conn:
    c.execute("""CREATE TABLE IF NOT EXISTS countries (
            country text,
            totalconfirmed integer
            )""")

#Store API response in a variable.
response_dict = r.json()
countries_dict = response_dict['Countries']

# Examine countries, total confirmed cases and add them to database
for country_info in countries_dict:
    country = country_info['Country']
    totalconfirmed = country_info['TotalConfirmed']
    with conn:
        c.execute("INSERT INTO countries VALUES(:country, :totalconfirmed)", {'country':country, 'totalconfirmed':totalconfirmed})

# Show top 10 countries by the number of cases.  
with conn:
    c.execute("SELECT * FROM countries ORDER BY totalconfirmed DESC")

first_ten_countries = c.fetchmany(10)

# Process results.
country, totalconfirmed = [], []
for country_name, total_cases in first_ten_countries:
    country.append(country_name)
    totalconfirmed.append(total_cases)

# Make visualization.
data = [{
    'type': 'bar',
    'x': country,
    'y': totalconfirmed,
}]

my_layout = {
    'title': 'Covid19 API Analysis',
    'xaxis': {'title': 'Countries'},
    'yaxis': {'title': 'Total Confirmed'},
}

fig = {'data': data, 'layout': my_layout}
offline.plot(fig, filename='covid19_api_analysis.html')

conn.close()
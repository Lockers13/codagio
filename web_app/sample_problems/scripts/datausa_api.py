from requests import get as rget
from json import loads as json_load

def get_population_data(url):

    query_params = {
        'drilldowns': 'State',
        'measures': 'Population',
        'year': 'latest'
    }

    data = json_load(rget(url, params=query_params).text)

    for row in data['data']:
        state = row.get('State')
        if state == 'Texas':
            year = row.get('Year')
            population = row.get('Population')
            print("Population of {0} in year {1} = {2}".format(state, year, population))

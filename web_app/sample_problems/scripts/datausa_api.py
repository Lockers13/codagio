from requests import get as rget
from json import loads as json_load

def get_population_data(init_data):
    url = init_data.get("url")
    q_params = init_data.get("q_params")
    data = json_load(rget(url, params=q_params).text)
    for row in data['data']:
        state = row.get('State')
        if state == 'Texas':
            year = row.get('Year')
            population = row.get('Population')
            print("Population of {0} in year {1} = {2}".format(state, year, population))

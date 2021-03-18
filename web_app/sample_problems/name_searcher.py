from json import loads as load_json

def name_searcher(targetfile, data):
    data = load_json(data)

    with open(targetfile, 'r') as f:
        name_set = set(load_json(f.read()))

    for name in data:
        print("{0} {1}".format(name, name in name_set))

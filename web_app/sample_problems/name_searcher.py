from json import loads as load_json

def name_searcher(targetfile, data):
    data = load_json(data)

    with open(targetfile, 'r') as f:
        name_set = set(load_json(f.read()))

    output_list = []
    
    for name in data:
        output_list.append("{0} {1}".format(name, name in name_set))
    
    return output_list

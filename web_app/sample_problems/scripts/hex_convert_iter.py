def hex_vert(inputs):
    ret_list = []

    for h_string in inputs:
        if h_string.startswith("0x"):
            try:
                ret_list.append("{0} : {1}".format(h_string, int(h_string, 16)))
            except ValueError as ve:
                ret_list.append("{0} : {1}".format(h_string, "Error: invalid characters"))
        else:
            ret_list.append("{0} : {1}".format(h_string, "Error: does not begin with a leading '0x'"))
            
    return ret_list
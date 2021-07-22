def hex_vert(inputs):
    for h_string in inputs:
        if h_string.startswith("0x"):
            try:
                print("{0} : {1}".format(h_string, int(h_string, 16)))
                continue
            except ValueError as ve:
                print("{0} : {1}".format(h_string, "Error: invalid characters"))
                continue
        else:
            print("{0} : {1}".format(h_string, "Error: does not begin with a leading '0x'"))
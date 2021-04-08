def hex_vert(h_string, data):
    given = data
    if h_string.startswith("0x"):
        try:
            return int(h_string, 16)
        except ValueError as ve:
            return "Error: the provided string contains invalid characters!"
    else:
        return "Error: the provided string does not begin with a leading '0x'"
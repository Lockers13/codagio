def list_functions_and_params(script):
    with open(script, 'r') as f:
        script_text = f.readlines()
        for line in script_text:
            private = False
            split_line = line.split()
            if len(split_line) > 0 and split_line[0] == "def":
                if split_line[1].startswith("_"):
                    private = True
                fname = split_line[1].split("(")[0]
                params = line.split("(")[1].split("):")[0].replace(", ", ",")
                print("{0}:{1}:{2}".format(fname, "private" if private else "public", params))

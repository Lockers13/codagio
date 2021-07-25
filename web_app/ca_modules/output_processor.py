from .subprocess_ctrl import run_subprocess_ctrld

def process_output(base_cmd, filename, input_arg=None, init_data=None):
    def clean_output(output):
        cleaned_split_output = output.decode("utf-8").replace('\r', '').splitlines()
        if cleaned_split_output[-1] == "None":
            cleaned_split_output = cleaned_split_output[:-1]
        ### clean up the returned output of subprocess - '\r' for windows, and 'None' because sometimes python sp.Popen adds this at the end (probably return value)

        ### uncomment below line for debugging
        # print("CSO =>", cleaned_split_output)
        return cleaned_split_output
    
    if init_data is not None:
        try:
            output = run_subprocess_ctrld(base_cmd, filename, input_arg=input_arg, init_data=init_data)
        except Exception as e:
            raise Exception("hhh{0}".format(str(e)))
    else:
        try:
            output = run_subprocess_ctrld(base_cmd, filename, input_arg=input_arg)
        except Exception as e:
            raise Exception("hhh{0}".format(str(e)))
    
    return clean_output(output)
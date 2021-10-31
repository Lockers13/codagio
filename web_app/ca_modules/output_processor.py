import subprocess
import os

def run_subprocess_ctrld(base_cmd, filename, input_arg=None, stage="verification", init_data=None):
    """Function for the running of subprocesses in a more controlled way, with various types of error checking + exception handling, &c.

    Returns the 'utf-8' decoded output of the run subprocess on success, exception is raised otherwise"""

    ### formatting of passed command string into argument for subprocees.Popen
    cmd_list = []
    for word in base_cmd.split(" "):
        cmd_list.append(word)
    ### filename and json input are passed separately and so must be individually appended to list
    ### we obviously do not want to split the json input on whitespace
    cmd_list.append(filename)

    if input_arg != None:
        cmd_list.append(input_arg)
    if init_data is not None:
        cmd_list.append(init_data)

    try:
        ### run subprocess, redirecting stdout to pipe to be read
        process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
    except Exception as e:
        raise Exception("YOYO" + str(e))
    ### crucially 'readlines()' and 'read()' are blocking for pipes
    output = process.stdout.read() if stage == "verification" else process.stdout.readlines()
    


    ### manually catch semantic error in submitted program by reading printed output that we control if an eexception is caught during its execution
    if stage == "verification":
        if b'EXCEPTION' in output:
            output = output.decode("utf-8").split('@')[1]
            raise Exception("{0}".format(str(output)))
    ### get return code of subprocess: if it is 124, then command has timed out - see 'man timeout'
    comm = process.communicate()[0]
    ret = int(process.returncode)
    if ret == 124:
        try:
            os.remove(filename)
            if os.path.isfile(input_arg):
                os.remove(input_arg)
        except Exception as e:
            pass
        raise Exception("Error during {0} stage - subprocess timed out: retcode = {1}".format(stage, ret))
    return output


def process_output(base_cmd, filename, input_arg=None, init_data=None, stage="verification"):
    def clean_output(output):
        if stage == "verification":
            cleaned_output = output.decode("utf-8").replace('\r', '').splitlines()
            if cleaned_output and cleaned_output[-1] == "None":
                cleaned_output = cleaned_output[:-1]
        elif stage == "memprof":
            cleaned_output = [out.decode("utf-8").strip('\n') for out in output]
        else:
            cleaned_output = output
        ### clean up the returned output of subprocess - '\r' for windows, and 'None' because sometimes python sp.Popen adds this at the end (probably return value)

        ### uncomment below line for debugging
        # print("CSO =>", cleaned_split_output)
        return cleaned_output
    
    if init_data is not None:
        try:
            output = run_subprocess_ctrld(base_cmd, filename, input_arg=input_arg, init_data=init_data, stage=stage)
        except Exception as e:
            raise Exception("{0}".format(str(e)))
    else:
        try:
            output = run_subprocess_ctrld(base_cmd, filename, input_arg=input_arg, stage=stage)
        except Exception as e:
            raise Exception("{0}".format(str(e)))
    
    return clean_output(output) ### Note: can't remember exactly why but the output of the profilers needs to be treated differently from that of the verifier
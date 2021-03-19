import subprocess
import os

def run_subprocess_ctrld(base_cmd, filename, json_arg, stage="verification", init_data=None):
    """Function for the running of subprocesses in a more controlled way, with various types of error checking + exception handling, &c.

    Returns the 'utf-8' decoded output of the run subprocess on success, exception is raised otherwise"""

    ### formatting of passed command string into argument for subprocees.Popen
    cmd_list = []
    for word in base_cmd.split(" "):
        cmd_list.append(word)
    ### filename and json input are passed separately and so must be individually appended to list
    ### we obviously do not want to split the json input on whitespace
    cmd_list.append(filename)

    cmd_list.append(json_arg)
    if init_data is not None:
        cmd_list.append(init_data)
    try:
        ### run subprocess, redirecting stdout to pipe to be read
        process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
    except Exception as e:
        raise Exception(str(e))
    ### crucially 'readlines()' and 'read()' are blocking for pipes
    output = process.stdout.read() if stage == "verification" else process.stdout.readlines()
    ### manually catch semantic error in submitted program by reading printed output that we control if an eexception is caught during its execution
    if stage == "verification":
        if b'EXCEPTION' in output:
            raise Exception("Exception: semantic error in submitted program")
    ### get return code of subprocess: if it is 124, then command has timed out - see 'man timeout'
    comm = process.communicate()[0]
    ret = int(process.returncode)
    if ret == 124:
        try:
            os.remove(filename)
        except:
            pass
        raise Exception("Error during {0} stage - subprocess timed out: retcode = {1}".format(stage, ret))
    return output
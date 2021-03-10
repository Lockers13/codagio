import subprocess
import os

def run_subprocess_ctrld(base_cmd, filename, json_arg, stage="verification"):
    cmd_list = []
    for word in base_cmd.split(" "):
        cmd_list.append(word)
    cmd_list.append(filename)
    cmd_list.append(json_arg)
    try:
        process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
    except Exception as e:
        raise Exception(str(e))

    output = process.stdout.read() if stage == "verification" else process.stdout.readlines()
    comm = process.communicate()[0]
    ret = int(process.returncode)
    if ret == 124:
        try:
            os.remove(filename)
        except:
            pass
        raise Exception("Error during {0} stage - subprocess timed out: retcode = {1}".format(stage, ret))
    return output
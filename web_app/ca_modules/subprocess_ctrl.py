import subprocess
import os

def run_subprocess_ctrld(timeout_dict, cmd, json, stage="verification"):
    cmd_list = [timeout_dict["keyword"], timeout_dict["timeout"]]
    for word in cmd.split(" "):
        cmd_list.append(word)
    filename = cmd_list[-1]
    cmd_list.append(json)
    try:
        process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
    except Exception as e:
        print("Exception in {0}, program processing stage:".format(stage), str(e))
        sys.exit(1)
    
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
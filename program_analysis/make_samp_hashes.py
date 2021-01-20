import sys
import subprocess
import hashlib

### Quick utility script to generate sample output hashes for a sample script specified on command line ###

try:
    prog_name = "sample_problems/{0}/{1}.py".format(sys.argv[1], sys.argv[1])
except IndexError:
    print("Error: incorrect number of clargs supplied")
    sys.exit(1)

hashes = []
for i in range(3):  
    s_process = subprocess.Popen(["python", prog_name, "{0}_input.json".format(prog_name.split(".")[0]), str(i)], stdout=subprocess.PIPE)
    output = s_process.stdout.read().decode("utf-8")
    output = output.replace(' ', '').replace('\n', '')
    samp_hash = hashlib.md5(output.encode()).hexdigest()
    hashes.append(samp_hash)

with open("{0}_hashes.txt".format(prog_name.split(".")[0]), 'w') as hf:
    for samp_hash in hashes:
        hf.write("{0}\n".format(samp_hash))

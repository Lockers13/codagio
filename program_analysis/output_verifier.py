import hashlib 
import subprocess
import sys

class Verifier:

    def __init__(self, filename):
        self.__filename = filename
        self.__sample_hashes = self.__get_sample_hashes()
        self.__sub_hashes = self.__gen_sub_hashes()

    def __gen_sub_hashes(self):
        sub_hashes = []
        # Note: number adjustable based on number of hash samples available
        for i in range(3):
            try:
                process = subprocess.Popen(["python", "{0}".format(self.__filename), "{0}_input{1}.txt".format(self.__filename.split(".")[0], i+1)], \
                     stdout=subprocess.PIPE)
            except Exception as e:
                print("Exception in verify_output, program processing stage:", str(e))
                sys.exit(1)

            output = process.stdout.read()
            stripped_sub = output.decode("utf-8").replace('\n', '').replace(' ', '')
            sub_hash = hashlib.md5(stripped_sub.encode()).hexdigest()
            sub_hashes.append(sub_hash)

        return sub_hashes

    def __get_sample_hashes(self):
        sample_hashes = []
        hash_filename = "{0}_hashes.txt".format(self.__filename.split(".")[0])
        with open(hash_filename, 'r') as hf:
            for line in hf:
                sample_hashes.append(line.strip('\n'))
        return sample_hashes

    def verify_output(self):
        score = 0
        for sub_hash, samp_hash in zip(self.__sub_hashes, self.__sample_hashes):
            if sub_hash == samp_hash:
                score += 1
        return "You scored: {0}%".format(round(score/len(self.__sample_hashes), 4) * 100)

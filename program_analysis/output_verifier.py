import hashlib 
import subprocess
import sys
import os

class Verifier:

    """Class for verifying output of submitted program, by checking against sample hashes

    previously generated via the relevant sample paragon program"""

    def __init__(self, analyzer):
        self.__filename, self.__simple_basename, self.__data_path = analyzer.get_paths()
        self.__program_dict = analyzer.get_prog_dict()
        
    def __gen_sub_hashes(self):
        """Private utility method to make hashes from output of provided submission program.

        Returns list of said hashes."""

        sub_hashes = []
        
        # Note: number adjustable...based on number of hash samples available for given problem
        for i in range(3):
            try:
                process = subprocess.Popen(["python", "{0}".format(self.__filename), "{0}_input.json".format(self.__data_path), str(i)], \
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
        """Private utility method to read in previously generated sample hashes from disk.

        Returns list of sample hashes."""

        sample_hashes = []
        hash_filename = "{0}_hashes.txt".format(self.__data_path)
        with open(hash_filename, 'r') as hf:
            for line in hf:
                sample_hashes.append(line.strip('\n'))
        return sample_hashes

    def verify_output(self):
        """Public method for verifying matches between hashes of submitted program's output, and sample hashes.

        Returns score as percentage (string) of exact hash matches."""

        sample_hashes = self.__get_sample_hashes()
        sub_hashes = self.__gen_sub_hashes()

        score = 0
        for sub_hash, samp_hash in zip(sub_hashes, sample_hashes):
            if sub_hash == samp_hash:
                score += 1
                
        self.__program_dict["score"] = "{0}%".format(round(score/len(sample_hashes), 4) * 100)
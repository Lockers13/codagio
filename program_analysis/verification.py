import hashlib 
import subprocess
import sys
import os
import json

class Verifier:

    """Class for verifying output of submitted program, by checking against sample hashes

    previously generated via the relevant sample paragon program"""

    def __init__(self, analyzer):
        self.__filename, self.__simple_basename, self.__data_path = analyzer.get_paths()
        self.__program_dict = analyzer.get_prog_dict()
        self.__args = analyzer.get_args()
        self.__num_tests = 3
        
    def __gen_sub_hashes(self):
        """Private utility method to make hashes from output of provided submission program.

        Returns list of said hashes."""

        sub_hashes = []
        
        # Note: number adjustable...based on number of hash samples available for given problem
        for i in range(self.__num_tests):
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

    def __detail_inputs(self, input_file):
        with open(input_file, 'r') as f:
            tests = json.loads(f.read())
            num_tests = len(tests)
            input_lengths = [len(inp) for inp in tests]
            input_types = [type(inp[0]).__name__.lower() for inp in tests]
            return num_tests, input_lengths, input_types
    
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
        self.__program_dict["scores"] = {}
        scores = self.__program_dict["scores"]
        test_stats = self.__detail_inputs("{0}_input.json".format(self.__data_path))

        overall_score = 0
        for count, (sub_hash, samp_hash) in enumerate(zip(sub_hashes, sample_hashes)):
            status = "success" if sub_hash == samp_hash else "failure"
            scores["test_{0}".format(count+1)] = {}
            test = scores["test_{0}".format(count+1)]
            test["status"] = status
            test["input_length"] = test_stats[1][count]
            test["input_type"] = test_stats[2][count]
            overall_score += 1

        scores["overall_score"] = "{0}%".format(round(overall_score/len(sample_hashes), 4) * 100)
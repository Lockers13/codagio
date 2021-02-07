import hashlib 
import subprocess
import sys
import os
import json

class Verifier:

    """Class for verifying output of submitted program, by checking against sample hashes

    previously generated via the relevant sample paragon program"""

    def __init__(self, analyzer, paragon):
        self.__filename = analyzer.get_filename()
        self.__program_dict = analyzer.get_prog_dict()
        self.__sample_hashes = json.loads(paragon.hashes)
        self.__sample_inputs = json.loads(paragon.inputs)
        self.__test_stats = self.__detail_inputs()
        
    def __gen_sub_hashes(self):
        """Private utility method to make hashes from output of provided submission program.

        Returns list of said hashes."""

        sub_hashes = []

        # Note: number adjustable...based on number of hash samples available for given problem
        for i in range(len(self.__sample_inputs)):
            try:
                process = subprocess.Popen(["python", "{0}".format(self.__filename), json.dumps(self.__sample_inputs[i])], \
                     stdout=subprocess.PIPE)
            except Exception as e:
                print("Exception in verify_output, program processing stage:", str(e))
                sys.exit(1)

            output = process.stdout.read()
            stripped_sub = output.decode("utf-8").replace('\n', '').replace(' ', '')
            sub_hash = hashlib.md5(stripped_sub.encode()).hexdigest()
            sub_hashes.append(sub_hash)

        return sub_hashes

    def __detail_inputs(self):
        num_tests = len(self.__sample_inputs)
        input_lengths = [len(inp) for inp in self.__sample_inputs]
        input_types = [type(inp[0]).__name__.lower() for inp in self.__sample_inputs]
        return num_tests, input_lengths, input_types
    
    def verify_output(self):
        """Public method for verifying matches between hashes of submitted program's output, and sample hashes.

        Returns score as percentage (string) of exact hash matches."""

        sample_hashes = self.__sample_hashes
        sub_hashes = self.__gen_sub_hashes()
        self.__program_dict["scores"] = {}
        scores = self.__program_dict["scores"]
        test_stats = self.__test_stats

        overall_score = 0
        for count, (sub_hash, samp_hash) in enumerate(zip(sub_hashes, sample_hashes)):
            if sub_hash == samp_hash:
                status = "success" 
                overall_score += 1
            else:
                status = "failure"
            scores["test_{0}".format(count+1)] = {}
            test = scores["test_{0}".format(count+1)]
            test["status"] = status
            test["input_length"] = test_stats[1][count]
            test["input_type"] = test_stats[2][count]

        percentage_score = round(overall_score/len(sample_hashes), 4) * 100
        scores["overall_score"] = "{0}%".format(percentage_score)

        return percentage_score
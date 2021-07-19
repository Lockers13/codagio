import hashlib 
import subprocess
import sys
import os
import json
import random
from .subprocess_ctrl import run_subprocess_ctrld
from django.utils.translation import gettext_lazy as _

class Verifier:

    """Class for verifying output of submitted program, by checking against sample outputs

    previously generated by the relevant sample reference program during problem upload"""

    def __init__(self, analyzer, problem_data):
        self.__filename = analyzer.get_filename()
        self.__program_dict = analyzer.get_prog_dict()
        self.__sample_outputs = problem_data["outputs"]
        self.__meta = problem_data["metadata"]
        self.__sample_inputs, self.__input_type = self.__get_sample_inputs_and_type(problem_data["inputs"])
        self.__init_data = problem_data["init_data"]

    def __get_sample_inputs_and_type(self, inputs):
        input_dict = inputs
        input_type = next(iter(input_dict))
        if input_type == "files":
            inputs = input_dict
        elif input_type == "default":
            inputs = input_dict[input_type]["custom"]
        elif input_type == "networking":
            inputs = input_dict
        return inputs, input_type

    def __gen_sub_outputs(self):
        """Private utility method to make hashes from output of provided submission program.

        Returns list of said hashes."""

        sub_outputs = []
        ### need to get underlying OS as syntax of timeout utility differs between linux and mac, and is nonexistent on windows
        platform = sys.platform.lower()
        VERIF_TIMEOUT = "5"
        VERIF_MEMOUT = "500"
        timeout_cmd = "gtimeout {0}".format(VERIF_TIMEOUT) if platform == "darwin" else "timeout {0} -m {1}".format(VERIF_TIMEOUT, VERIF_MEMOUT) if platform == "linux" or platform == "linux2" else ""
        base_cmd = "{0} python".format(timeout_cmd)
        file_list = []

        ### if input_type is 'file', then iterate over input dict, writing each file to disk as 'file1, file2, filen'
        if self.__input_type == "files":
            for i in range(len(self.__sample_inputs["files"].keys())):
                key = "file_{0}".format(i+1) 
                with open("{0}.py".format(key), 'w') as f:
                    f.write(self.__sample_inputs["files"][key])
                file_list.append("{0}.py".format(key))
            for target_file in file_list:
                if self.__init_data is not None:
                    try:
                        output = run_subprocess_ctrld(base_cmd, self.__filename, target_file, init_data=self.__init_data)
                    except Exception as e:
                        raise Exception("hhh{0}".format(str(e)))
                else:
                    try:
                        output = run_subprocess_ctrld(base_cmd, self.__filename, target_file)
                    except Exception as e:
                        raise Exception("hhh{0}".format(str(e)))           
                ### clean up the returned output of subprocess - '\r' for windows, and 'None' because sometimes python sp.Popen adds this at the end (probably return value)
                cleaned_split_output = output.decode("utf-8").replace('\r', '').splitlines()
                if cleaned_split_output[-1] == "None":
                    cleaned_split_output = cleaned_split_output[:-1]
                ### uncomment below line for debugging
                # print("CSO =>", cleaned_split_output)
                sub_outputs.append(cleaned_split_output)
                ### remove throwaway files after uploaded script has been run on them => if they exist!
                os.remove(target_file)
            return sub_outputs
        elif self.__input_type == "default":
            for i in range(len(self.__sample_inputs)):
                if self.__init_data is not None:
                    try:
                        output = run_subprocess_ctrld(base_cmd, self.__filename, json.dumps(self.__sample_inputs[i]), init_data=self.__init_data)
                    except Exception as e:
                        raise Exception("{0}".format(str(e)))
                else:
                    try:
                        output = run_subprocess_ctrld(base_cmd, self.__filename, json.dumps(self.__sample_inputs[i]))
                    except Exception as e:
                        raise Exception("{0}".format(str(e)))                   
                ### clean up the returned output of subprocess - '\r' for windows, and 'None' because sometimes python sp.Popen adds this at the end (probably return value)
                cleaned_split_output = output.decode("utf-8").replace('\r', '').splitlines()
                if cleaned_split_output[-1] == "None":
                    cleaned_split_output = cleaned_split_output[:-1]
                ### uncomment below line for debugging
                # print("CSO =>", cleaned_split_output)
                sub_outputs.append(cleaned_split_output)
                ### remove throwaway files after uploaded script has been run on them => if they exist!
            return sub_outputs
        elif self.__input_type == "networking":
            urls = self.__sample_inputs["networking"]["urls"]
            for url in urls:
                try:
                    output = run_subprocess_ctrld(base_cmd, self.__filename, url)
                except Exception as e:
                    raise Exception("{0}".format(str(e)))   
                cleaned_split_output = output.decode("utf-8").replace('\r', '').splitlines()
                if cleaned_split_output[-1] == "None":
                    cleaned_split_output = cleaned_split_output[:-1]
                ### uncomment below line for debugging
                # print("CSO =>", cleaned_split_output)
                sub_outputs.append(cleaned_split_output)
                ### remove throwaway files after uploaded script has been run on them => if they exist!
            return sub_outputs
            

    def __detail_inputs(self):
        """Utility function to get info about input type, length, etc.

        Returns tuple of relevant datapoints"""

        if self.__input_type == "files":
            num_tests = len(self.__sample_inputs["files"].keys())
            ### get number of lines in each file (in a list => [len(file1), len(file2), len(fileN)])
            num_keys = len(self.__sample_inputs["files"].keys())
            input_lengths = ["# lines: {0}".format(len(self.__sample_inputs["files"]["file_{0}".format(i+1)].splitlines())) for i in range(num_keys)]
            input_types = ["file" for x in range(num_tests)]
        elif self.__input_type == "default":
            num_tests = len(self.__sample_inputs)
            input_lengths = [len(inp) for inp in self.__sample_inputs]
            input_types = [type(inp[0]).__name__.lower() for inp in self.__sample_inputs]
        elif self.__input_type == "networking":
            num_tests = 1
            input_lengths = ["API URL"]
            input_types = ["url"]

        return num_tests, input_lengths, input_types
    
    def verify_output(self):
        """Public method for verifying matches between submitted program's output, and sample outputs.

        Returns score as percentage (string) of exact matches (this point may need reviewing)."""
        
        def get_result_stats():
            num_outputs = len(sub_output)
            result_dict = {}
            mismatches = []
            matches = []
            for line_count, (line_sub, line_samp) in enumerate(zip(sub_output, samp_output)):
                if line_sub != line_samp:
                    mismatches.append((line_sub, line_samp))
                else:
                    matches.append(line_sub)
            num_correct = len(matches)
            result_dict["num_correct"] = num_correct
            try:
                result_dict["success_rate"] = round(num_correct/num_outputs, 4) * 100
            except Exception as e:
                result_dict["success_rate"] = "File IO"
            num_failures = len(mismatches)
            result_dict["num_failures"] = num_failures
            result_dict["num_tests"] = test_stats[1][count]
            try:
                result_dict["failure_rate"] = round((int(num_failures)/num_outputs), 4) * 100
            except Exception as e:
                result_dict["failure_rate"] = "File IO"
            num_fail_samples = 5 if num_failures > 3 else num_failures
            num_correct_samples = 5 if num_correct > 3 else num_correct
            result_dict["mismatches"] = random.sample(mismatches, num_fail_samples)
            result_dict["matches"] = random.sample(matches, num_correct_samples)
            return result_dict

        sample_outputs = self.__sample_outputs
        print("SAMPOUT =>", sample_outputs)
        sub_outputs = self.__gen_sub_outputs()
        print("SUBOUT =>", sub_outputs)
        self.__program_dict["scores"] = {}
        scores = self.__program_dict["scores"]
        ### stores input details (cf. __init__)
        test_stats = self.__detail_inputs()

        overall_score = 0
        ### loop to compare sub output with sample output in one go, as if they were two columns, one beside the other
        for count, (sub_output, samp_output) in enumerate(zip(sub_outputs, sample_outputs)):
            result_dict = get_result_stats()
            status = "success" if result_dict["success_rate"] == 100 else "failure"
            scores["test_{0}".format(count+1)] = {}
            test = scores["test_{0}".format(count+1)]
            test["status"] = status
            test["input_length"] = test_stats[1][count]
            test["input_type"] = test_stats[2][count]
            test["detailed_stats"] = result_dict
            overall_score += result_dict["success_rate"] / 100

        ### store score as string
        percentage_score = round(overall_score/len(sample_outputs), 4) * 100
        scores["overall_score"] = "{0}%".format(percentage_score)
        ### since all pertinent data is written to program dict, we can just return the score here, for code_analysis.views to handle
        return percentage_score
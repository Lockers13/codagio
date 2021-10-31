import subprocess
import os
import platform
import re
import json
import sys
from .output_processor import process_output

class Profiler:

    def __init__(self, analyzer, problem_data):
        self.__filename = analyzer.get_filename()
        self.__program_dict = analyzer.get_prog_dict()
        self.__udef_info = self.__get_udef_info()
        self.__input_type = next(iter(problem_data["metadata"]["input_type"]))
        self.__sample_inputs = problem_data["inputs"]
        self.__init_data = problem_data["init_data"]
        self.__num_tests = problem_data["metadata"]["num_tests"]
        self.__offset = 3 ### this is the number of lines added during preprocessing, whereas calculation of function lineno during ast_visitor stage happens prior to preprocessing, so it must be offset
    ### metadata is not passed into profiler, so we get the input type by checking the key of the input dict
    ### Note: auto generated input should also be passed to DB as lists inside a dict with key 'auto' => this mod will require changes in several places
    
    def __remove_files(self, *args):
        for f in args:
            try:
                os.remove(f)
            except FileNotFoundError:
                pass

    def __get_udef_info(self):
        """Utility method to make user function defintiion info collected by ast visitor more easily accessible.

        Called once from __init__ : returns dict having elements of form {fname: [fdef_key, lineno]}"""

        fdefs = self.__program_dict["fdefs"]
        return {fdefs[fdef_key]["name"]: [fdef_key, fdefs[fdef_key]["lineno"]] \
            for fdef_key in fdefs.keys()}

    def lprof(self):
        """Line by line profiling method.

        Returns None, writes output to global program dict"""

        def make_pro_file(filename, lines, token):
            """Internal helper function; creates file to be profiled by kernprof by inserting 
            
            '@profile' decorators at appropriate points in original source file. Returns name of file to be profiled"""

            f = open(filename, "r")
            contents = f.readlines()
            f.close()

            profiled_lines = 0

            for lineno in lines:
                # get insertion position 
                # (-1 for zero based, + profiled lines as each insertion increases number of lines in file by 1)
                pos = lineno - 1 + profiled_lines
                # calculate necessary indentation for '@profile' insertion, as number of spaces
                num_spaces = len(contents[pos]) - len(contents[pos].lstrip())
                contents.insert(pos, "{0}{1}\n".format(" " * num_spaces, token))
                profiled_lines += 1

            # make separate profiling file and write data to it
            split_fname = filename.split(".")
            pro_file = "{0}_profile.{1}".format(split_fname[0],split_fname[1])
            f = open(pro_file, "w")
            contents = "".join(contents)
            f.write(contents)
            f.close()

            return pro_file

        def do_profile(pro_file):
            """Function which calls kernprof subprocess, parses its output, 
            and writes results to fdef subdicts of global program dict.
            
            Returns None"""

            def process_lprof_out(output):
                """Helper function for processing the bytes output piped in from kernprof.

                Returns None"""

                def write_lprofs(reached=True):
                    """Helper function for actual writing of lprof results to appropriate subdicts

                    Returns None"""
                    
                    ### NB: The times recorded by lprof tool are  misleading due to the overhead incurred by the 
                    ### operation of the tool itself. However, lprof also records a propotional measure of time spent 
                    ### inside a function (%time). So we use this latter, in conjunction with the results returned by cProfile
                    ### to get a more accurate estimate of real time spent executing each line.
                    ### viz. real_time_per_line = %time in line (lprof) * total cumulative function time (cProf)
                    
                    fdefs[fdef_k]["line_profile"]["line_{0}".format(int(split_line[0]) - fnum)] = {}
                    line_info = fdefs[fdef_k]["line_profile"]["line_{0}".format(int(split_line[0]) - fnum)]
                    if reached:
                        try:
                            line_info["hits"] = float(split_line[1])
                            line_info["%time"] = float(split_line[4])
                            line_info["contents"] = split_line[5]
                            line_info["real_time"] = str(round(float(fdefs[fdef_k]["cum_time"]) * float(split_line[4])/100, 6))
                        except Exception as e:
                            new_split = line.split(maxsplit=1)
                            line_info["hits"] = "0"
                            line_info["%time"] = "0.0"
                            line_info["contents"] = new_split[1]
                            line_info["real_time"] = "0.0"
                    else:
                        line_info["hits"] = "0"
                        line_info["%time"] = "0.0"
                        contents = "" if split_line[1] == "0.0" else split_line[1]
                        line_info["contents"] = contents
                        line_info["real_time"] = "0.0"

                fdefs = self.__program_dict["fdefs"]
                in_func = False
                for line in output:
                    # received bytes need decoding
                    line = line.decode("utf-8").strip()
                    split_line = line.split(maxsplit=5)
                    len_sl = len(split_line)
                    if len_sl == 0:
                        in_func = False
                    elif split_line[0].startswith("======"):
                        in_func = True
                    elif not in_func:
                        pass
                    elif "@profile" in split_line:
                        pass
                    elif len_sl > 1 and len_sl < 6:
                        if split_line[1].startswith("def"):
                            fname = split_line[2].split("(")[0]
                            fdef_k = self.__udef_info[fname][0]
                            fdefs[fdef_k]["line_profile"] = {}
                            fnum = int(re.search(r'\d+', fdef_k).group())
                        split_line = " ".join(split_line).split(maxsplit=1)
                        split_line.append("0.0")
                        write_lprofs(reached=False)
                    elif len_sl == 6:
                        write_lprofs()

            # ! below is useful for debugging problems with line_profiler! ###
            # with open(pro_file, 'r') as f:
            #     for line in f.readlines():
            #         print(line)
            
            platform = sys.platform.lower()
            LPROF_TIMEOUT = "12"
            LPROF_MEMOUT = "1000"
            # call kernprof as subprocess, redirecting stdout to pipe, and read results
            timeout_cmd = "gtimeout {0}".format(LPROF_TIMEOUT) if platform == "darwin" else "timeout {0} -m {1}".format(LPROF_TIMEOUT, LPROF_MEMOUT) if platform == "linux" or platform == "linux2" else ""

            base_cmd = "{0} kernprof -l -v".format(timeout_cmd)

            if self.__input_type == "file":
                with open('lprof_script.py', 'w') as f:
                    f.write(self.__sample_inputs["files"]["file_1"])
                output = process_output(base_cmd, pro_file, input_arg="lprof_script.py", init_data=self.__init_data, stage="line_profile")
                os.remove("lprof_script.py")
            elif self.__input_type == "default":
                input_arg = json.dumps(self.__sample_inputs[0]) if self.__sample_inputs is not None else None
                # crucially, readlines() is blocking for pipes
                output = process_output(base_cmd, pro_file, input_arg=input_arg, init_data=self.__init_data, stage="line_profile")
            process_lprof_out(output)

            ### clean up ###
            
            # remove file with '@profile'
            self.__remove_files(pro_file, "{0}.lprof".format(os.path.basename(pro_file)))
    
        # check that line profiler is installed for kernprof
        try:
            import line_profiler
        except ModuleNotFoundError:
            raise Exception("Error: line_profiler module must be installed for line-by-line profiling!")

        # get udef linenos from self.udef_info as defined above
        udef_lines = [(self.__udef_info[fdef_name][1] + self.__offset) for fdef_name in self.__udef_info.keys()]
        pro_token = "@profile"
        pro_file = make_pro_file(self.__filename, udef_lines, pro_token)
        do_profile(pro_file)

        ### Note: Line_Profiler output header => Line #: Hits: Time: Per Hit: % Time: Line Contents
            
    def cprof(self):
        """Method which writes cProfile stats (function by function, rather than line by line) to appropriate fdef subdicts.

        Returns None"""

        def process_cprof_out(output):
            """Helper function for processing the bytes output piped in from cProfile.

            Returns None"""
            
            udef_names = self.__udef_info.keys()
            fdefs = self.__program_dict.get("fdefs")

            # parse output of external cProfile program and write all pertinent results to appropriate fdef subdict
            for line in output:
                line = line.decode("utf-8").strip()
                try:
                    u_fname = re.search('\(([^)]+)', line.split()[5]).group(1)
                    if u_fname in udef_names:
                        split_line = line.split()
                        fdef_k = self.__udef_info[u_fname][0]
                        fdefs[fdef_k]["ncalls"] = split_line[0]
                        fdefs[fdef_k]["tot_time"] = split_line[1]
                        fdefs[fdef_k]["cum_time"] = split_line[3]
                        self.__program_dict["udef_func_time_tot"] += round(float(split_line[3]), 5)
                except Exception as e:
                    pass

        platform = sys.platform.lower()
        CPROF_TIMEOUT = "10"
        CPROF_MEMOUT = "1000"
        # call cProfile as subprocess, redirecting stdout to pipe, and read results, as before
        timeout_cmd = "gtimeout {0}".format(CPROF_TIMEOUT) if platform == "darwin" else "timeout {0} -m {1}".format(CPROF_TIMEOUT, CPROF_MEMOUT) if platform == "linux" or platform == "linux2" else ""
        base_cmd = "{0} python -m cProfile -s time".format(timeout_cmd) 
        if self.__input_type == "file":
            with open('cprof_script.py', 'w') as f:
                f.write(self.__sample_inputs["files"]["file_1"])
            output = process_output(base_cmd, self.__filename, input_arg="cprof_script.py", init_data=self.__init_data, stage="c_profile")
            self.__remove_files("cprof_script.py")
        elif self.__input_type == "default":
            input_arg = json.dumps(self.__sample_inputs[0]) if self.__sample_inputs is not None else None
            output = process_output(base_cmd, self.__filename, input_arg=input_arg, init_data=self.__init_data, stage="c_profile")


        process_cprof_out(output)

    def gnu_time_stats(self):
        """Method which writes global program performance stats to program dict.

        Returns None"""

        # check for underlying OS
        time_cmd = "gtime" if platform.system() == "Darwin" else "time"
        prog_dict = self.__program_dict
        # open devnull, to redirect stdout to oblivion, since with gnu time, the important output is written to stderr
        dev_null = open(os.devnull, 'w')
        # call gnu time as subprocess, redirecting stdout to /dev/null and stderr to pipe, and read results, as before
        process = subprocess.Popen([time_cmd,  "--verbose", "python", "{0}".format(self.__filename)], stderr=subprocess.PIPE, stdout=dev_null)
        dev_null.close()
        output = process.stderr.readlines()

        # again parse output of external profiling program and write all pertinent results to global prog ddict
        for line in output:
            line = line.decode("utf-8").strip()
            split_line = line.split(": ")
            try:
                prog_dict["{0}".format(str(split_line[0]))] = float(split_line[1])
            except:
                pass

    def memprof(self):
        def make_pro_file(filename):
            with open(filename, "r") as f:
                contents = f.readlines()
            
            import_insert = "import os\nimport psutil\n"
            profile_insert = "{0}print('MEMORYSTATS')\n{1}print(round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, 2))\n{2}print(round(psutil.Process(os.getpid()).memory_info().vms / 1024 ** 2, 2))\n".format(" " * 8, " " * 8, " " * 8)
            contents.insert(0, import_insert)
            main_insert_idx = contents.index("{0}### insert memprof ###\n".format(" " * 8)) + 1

            # len_con = len(contents)
            # if contents[len_con - 1] != "\n":
            #     contents.insert(len_con, "\n")
            #     len_con += 1

            contents.insert(main_insert_idx, profile_insert)
        
            split_fname = filename.split(".")
            pro_file = "{0}_memprof.{1}".format(split_fname[0],split_fname[1])
            with open(pro_file, "w") as g:
                g.write("".join(contents))
            
            return pro_file

        pro_file = make_pro_file(self.__filename)
        if self.__input_type == "file":
            with open("memprof_script.py", 'w') as f:
                f.write(self.__sample_inputs["files"]["file_1"])
            output = process_output("python", pro_file, input_arg="memprof_script.py", init_data=self.__init_data, stage="memprof")
            mem_init_idx = output.index("MEMORYSTATS")
            self.__program_dict["total_physical_mem"] = float(output[mem_init_idx + 1])
            self.__program_dict["total_virtual_mem"] = float(output[mem_init_idx + 2])
            
        elif self.__input_type == "default":
            input_arg = json.dumps(self.__sample_inputs[0]) if self.__sample_inputs is not None else None
            output = process_output("python", pro_file, input_arg=input_arg, init_data=self.__init_data, stage="memprof")
            mem_init_idx = output.index("MEMORYSTATS")
            self.__program_dict["total_physical_mem"] = float(output[mem_init_idx + 1])
            self.__program_dict["total_virtual_mem"] = float(output[mem_init_idx + 2])

        self.__remove_files(pro_file, "memprof_script.py")
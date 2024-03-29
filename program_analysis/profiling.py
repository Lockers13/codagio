import subprocess
import os
import platform
import re

class Profiler:

    def __init__(self, analyzer):
        self.__filename, self.__simple_basename, self.__data_path = analyzer.get_paths()
        self.__program_dict = analyzer.get_prog_dict()
        self.__udef_info = self.__get_udef_info()
        self.__args = analyzer.get_args()

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
                        line_info["hits"] = split_line[1]
                        line_info["%time"] = split_line[4]
                        line_info["contents"] = split_line[5]
                    else:
                        line_info["hits"] = "0"
                        line_info["%time"] = "0.0"
                        contents = "" if split_line[1] == "0.0" else split_line[1]
                        line_info["contents"] = contents

                fdefs = self.__program_dict["fdefs"]
                in_func = False
                for line in output:
                    # received bytes need decoding
                    line = line.decode("utf-8").strip()
                    split_line = line.split(maxsplit=5)
                    len_sl = len(split_line)
                    if len_sl == 0:
                        in_func = False
                    elif split_line[0].startswith("=============================================="):
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
            
            # call kernprof as subprocess, redirecting stdout to pipe, and read results
            process = subprocess.Popen(["kernprof", "-l", "-v", "{0}".format(pro_file), "{0}_input.json".format(self.__data_path), "1"], stdout=subprocess.PIPE)
            # crucially, readlines() is blocking for pipes
            output = process.stdout.readlines()
            process_lprof_out(output)

            ### clean up ###
            # remove file with '@profile' 
            os.remove(pro_file)
            # remove auto generated lprof output file
            os.remove("{0}.lprof".format(os.path.basename(pro_file)))
    
        # check that line profiler is installed for kernprof
        try:
            import line_profiler
        except ModuleNotFoundError:
            print("Error: line_profiler module must be installed for line-by-line profiling!")
            return

        # get udef linenos from self.udef_info as defined above
        udef_lines = [self.__udef_info[fdef_name][1] for fdef_name in self.__udef_info.keys()]
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
                except Exception as e:
                    pass

        # call cProfile as subprocess, redirecting stdout to pipe, and read results, as before
        process = subprocess.Popen(["python", "-m", "cProfile", "-s", "time", "{0}".format(self.__filename), "{0}_input.json".format(self.__data_path), "1"], stdout=subprocess.PIPE)
        output = process.stdout.readlines()

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
            profile_insert = "print(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2)\nprint(psutil.Process(os.getpid()).memory_info().vms / 1024 ** 2)"
            contents.insert(0, import_insert)

            len_con = len(contents)
            if contents[len_con - 1] != "\n":
                contents.insert(len_con, "\n")
                len_con += 1

            contents.insert(len_con, profile_insert)

            split_fname = filename.split(".")
            pro_file = "{0}_memprof.{1}".format(split_fname[0],split_fname[1])
            print("".join(contents))
            with open(pro_file, "w") as g:
                g.write("".join(contents))
            
            return pro_file

        pro_file = make_pro_file(self.__filename)

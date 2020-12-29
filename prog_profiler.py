import subprocess
import os
import platform
import re

class Profiler():

    def __init__(self, filename, program_dict):
        self.filename = filename
        self.program_dict = program_dict
        self.udef_info = self.__get_udef_info()

    def __get_udef_info(self):
        fdefs = self.program_dict["fdefs"]
        return {fdefs[fdef_key]["name"]: [fdef_key, fdefs[fdef_key]["lineno"]] \
            for fdef_key in fdefs.keys()}

    def __lprof(self):
        ### Note: check if line_profiler is installed
        def make_pro_file(filename, lines, token):
            f = open(filename, "r")
            contents = f.readlines()
            f.close()

            profiled_lines = 0

            for lineno in lines:
                num_spaces = len(contents[lineno-1+profiled_lines]) - len(contents[lineno-1+profiled_lines].lstrip())
                contents.insert((lineno-1) + profiled_lines, "{0}{1}\n".format(" "*num_spaces, token))
                profiled_lines += 1

            split_fname = filename.split(".")
            pro_file = "{0}_profile.{1}".format(split_fname[0],split_fname[1])
            f = open(pro_file, "w")
            contents = "".join(contents)
            f.write(contents)
            f.close()

            return pro_file

        def parse_pro_file(pro_file):
            def write_lprofs():
                float(second_item)
                fdefs[fdef_k]["line_profile"]["line_{0}".format(int(split_line[0]) - fnum)] = {}
                tot_time = fdefs[fdef_k]["tot_time"]
                cum_time = fdefs[fdef_k]["cum_time"]
                line_info = fdefs[fdef_k]["line_profile"]["line_{0}".format(int(split_line[0]) - fnum)]
                line_info["hits"] = split_line[1]
                line_info["time"] = '%.2E' % ((float(split_line[4])/100) * float(cum_time))
                line_info["time_per_hit"] = '%.2E' % (float(line_info["time"]) / float(line_info["hits"]))
                line_info["%time"] = split_line[4]
                line_info["contents"] = split_line[5]
            
            process = subprocess.Popen(["kernprof", "-l", "-v", "{0}".format(pro_file)], stdout=subprocess.PIPE)
            output = process.stdout.readlines()
            fdefs = self.program_dict["fdefs"]
 
            for line in output:
                line = line.decode("utf-8").strip()
                split_line = line.split(maxsplit=5)

                try:
                    first_item, second_item = split_line[0], split_line[1]
                except IndexError:
                    continue

                if len(split_line) == 6 or first_item == "Total" or first_item == "Function:":
                    if first_item == "Function:":
                        fname = split_line[1]
                        fdef_k = self.udef_info[fname][0]   
                        fdefs[fdef_k]["line_profile"] = {}
                        fnum = int(re.search(r'\d+', fdef_k).group())
                    else:
                        try:
                            write_lprofs()
                        except Exception as e:
                            continue
                else:
                    continue
        
        try:
            import line_profiler
        except ModuleNotFoundError:
            print("Error: line_profiler module must be installed for line-by-line profiling!")
            return

        udef_lines = [self.udef_info[fdef_name][1] for fdef_name in self.udef_info.keys()]
        pro_token = "@profile"
        pro_file = make_pro_file(self.filename, udef_lines, pro_token)
        parse_pro_file(pro_file)

        ### Line_Profiler output header => Line #: Hits: Time: Per Hit: % Time: Line Contents
            
    def __cprof(self):
        process = subprocess.Popen(["python", "-m", "cProfile", "-s", "time", "{0}".format(self.filename)], stdout=subprocess.PIPE)
        output = process.stdout.readlines()

        udef_names = self.udef_info.keys()
        fdefs = self.program_dict.get("fdefs")
        ### Note : watch for unintentionally long output ###
        for line in output:
            line = line.decode("utf-8").strip()
            try:
                u_fname = re.search('\(([^)]+)', line.split()[5]).group(1)
                if u_fname in udef_names:
                    split_line = line.split()
                    fdef_k = self.udef_info[u_fname][0]
                    fdefs[fdef_k]["ncalls"] = split_line[0]
                    fdefs[fdef_k]["tot_time"] = split_line[1]
                    fdefs[fdef_k]["cum_time"] = split_line[3]
            except Exception as e:
                pass
            
    def __gnu_time_stats(self):
        time_cmd = "gtime" if platform.system() == "Darwin" else "time"
        prog_dict = self.program_dict
        dev_null = open(os.devnull, 'w')
        process = subprocess.Popen([time_cmd,  "--verbose", "python", "{0}".format(self.filename)], stderr=subprocess.PIPE, stdout=dev_null)
        dev_null.close()
        output = process.stderr.readlines()

        for line in output:
            line = line.decode("utf-8").strip()
            split_line = line.split(": ")
            try:
                prog_dict["{0}".format(str(split_line[0]))] = float(split_line[1])
            except:
                pass

    def profile(self, args):
        self.__cprof()
        if args.get("g"):
            self.__gnu_time_stats()
        self.__lprof()
        ### And so on ###    
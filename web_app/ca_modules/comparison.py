import json
import os

class Comparer:

    def __init__(self, analyzer):
        self.__filename, self.__simple_basename, self.__data_path = analyzer.get_paths()
        self.__sub_analysis = analyzer.get_prog_dict()
        self.__samp_analysis = self.__get_sample_analysis()
        self.__sub_fdefs, self.__samp_fdefs = self.__sub_analysis["fdefs"], self.__samp_analysis["fdefs"]
        self.__args = analyzer.get_args()

    def __get_sample_analysis(self):
        with open("{0}_analysis.json".format(self.__data_path), 'r') as f:
            samp_analysis = json.loads(f.read())
        return samp_analysis 

    def __print_test_stats(self):
        scores = self.__sub_analysis["scores"]
        print("Displaying test stats breakdown\n------------------------------------------")
        for k, v in scores.items():
            if k == "overall_score":
                continue
            print("\n{0}:\n".format(k.capitalize()))
            print("Status => {0}".format(v["status"]))
            print("Input Length => {0}".format(v["input_length"]))
            print("Input Type => {0}".format(v["input_type"]))          
        print("\nOverall Score = {0}".format(self.__sub_analysis["scores"]["overall_score"]))
    
    def __display_lprof_stats(self):
        for k, v in self.__sub_fdefs.items():
            fname = v["name"]
            lprof_dict = v["line_profile"]
            cum_time = float(v["cum_time"])
            # Note: we need to normalise percentages due to overhead introduced by profiling in case they do not total to 100%, or some value near enough
            percentage_time = sum([float(val["%time"]) for val in lprof_dict.values()])
            accumulator = 0

            first = True
            print("\nDisplaying lprof stats for function '{0}'".format(fname))
            print("--------------------------------------------------------")
            for inner_k, inner_v in lprof_dict.items():
                line_no = int(inner_k.split("_")[1])
                if first:
                    offset = line_no - 1
                    first = False
                # see: normalisation note above
                p_time = (float(inner_v["%time"])/percentage_time) * 100 if abs(percentage_time - 100) > 1 else float(inner_v["%time"]) 
                print("Line {0} -  Contents: '{1}'\n=> Percentage Time: {2}, Real Time: {3}, Hits: {4}\n".format(
                    line_no - offset,
                    inner_v["contents"],
                    inner_v["%time"],
                    '%.2E' % ((p_time/100) * cum_time),
                    inner_v["hits"]
                    )
                )
                accumulator += (p_time/100) * cum_time

            # Test => print("\nCprof cum time : {0} vs. Calculated cum time : {1}".format(cum_time, accumulator))

    def __show_logical_skeletons(self):
        def print_skeleton(fdef_dict):
            for k, v in fdef_dict.items():
                skeleton = v["skeleton"]
                print(skeleton[0])
                for skel in skeleton[1:]:
                    print(skel)

        print("\nDisplaying logical skeleton of sample:\n------------------------------------------")
        print_skeleton(self.__samp_fdefs)
        print("\nDisplaying logical skeleton of submission:\n------------------------------------------")
        print_skeleton(self.__sub_fdefs)

    def __compare_fdef_stats(self):
        """

        Returns a list of lists containing pairwise comparison stats.
        """
        def ziplist_stats(sub, samp):
            print("\nDisplaying global stats (cprof)...\n\nSubmission\t|\tSample\n------------------------------------------------")
            fdef_comp_stats = []
            for (k1, v1), (k2, v2) in zip(sub.items(), samp.items()):
                if not isinstance(v1, dict) and not isinstance(v2, dict) and (k1 != "skeleton" and k2 != "skeleton"):
                    inner_comp = []
                    sub_stats = "{0} : {1}".format(k1, v1)
                    sample_stats = "{0} : {1}".format(k2, v2)
                    inner_comp.append(sub_stats)
                    inner_comp.append(sample_stats)
                    print("{0} | {1}".format(sub_stats, sample_stats))
                    fdef_comp_stats.append(inner_comp)
            print()
            return fdef_comp_stats

        fdef_comp = []
        for (k1, v1), (k2, v2) in zip(self.__sub_fdefs.items(), self.__samp_fdefs.items()):
            fdef_comp.append(ziplist_stats(v1, v2))
        return fdef_comp

    def compare(self):
        self.__sub_analysis["fcomp_overview_stats"] = self.__compare_fdef_stats()
        self.__print_test_stats()
        self.__show_logical_skeletons()
        if self.__args.get("l"):
            self.__display_lprof_stats()
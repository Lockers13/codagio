import json
import os

class Comparer:

    def __init__(self, analyzer):
        self.__filename, self.__simple_basename, self.__data_path = analyzer.get_paths()
        self.__sub_analysis = analyzer.get_prog_dict()
        self.__samp_analysis = self.__get_sample_analysis()
        self.__args = analyzer.get_args()

    def __get_sample_analysis(self):
        with open("{0}_analysis.json".format(self.__data_path), 'r') as f:
            samp_analysis = json.loads(f.read())
        return samp_analysis 

    def __print_test_stats(self):
        scores = self.__sub_analysis["scores"]
        print("\nTest stats breakdown\n------------------------------------------")
        for k, v in scores.items():
            if k == "overall_score":
                continue
            print("\n{0}:\n".format(k.capitalize()))
            print("Status => {0}".format(v["status"]))
            print("Input Length => {0}".format(v["input_length"]))
            print("Input Type => {0}".format(v["input_type"]))          
        print("\nOverall Score = {0}".format(self.__sub_analysis["scores"]["overall_score"]))
    
    def __display_lprof_stats(self):
        sub_fdefs = self.__sub_analysis["fdefs"]
        for k, v in sub_fdefs.items():
            fname = v["name"]
            lprof_dict = v["line_profile"]
            first = True
            print("\nDisplaying lprof stats for function '{0}'".format(fname))
            print("--------------------------------------------------------")
            for inner_k, inner_v in lprof_dict.items():
                line_no = int(inner_k.split("_")[1])
                if first:
                    offset = line_no - 1
                    first = False
                print("Line {0} - Hits: {1}, Percentage Time: {2}, Contents: {3}".format(
                    line_no - offset,
                    inner_v["hits"],
                    inner_v["%time"],
                    inner_v["contents"]
                    )
                )

    def __show_logical_skeletons(self):
        def print_skeleton(fdef_dict):
            for k, v in fdef_dict.items():
                skeleton = v["skeleton"]
                print(skeleton[0])
                for skel in skeleton[1:]:
                    print(skel)

        samp_fdefs = self.__samp_analysis["fdefs"]
        sub_fdefs = self.__sub_analysis["fdefs"]
        print("\nDisplaying logical skeleton of sample:\n------------------------------------------")
        print_skeleton(samp_fdefs)
        print("\nDisplaying logical skeleton of submission:\n------------------------------------------")
        print_skeleton(sub_fdefs)

    def __compare_fdef_stats(self):
        """

        Returns a list of lists containing pairwise comparison stats.
        """
        def ziplist_stats(sub, samp):
            print("\nDisplaying global stats (no lprof)...\n\nSubmission\t|\tSample\n------------------------------------------------")
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

        sub_fdefs, samp_fdefs = self.__sub_analysis["fdefs"], self.__samp_analysis["fdefs"]
        fdef_comp = []
        for (k1, v1), (k2, v2) in zip(sub_fdefs.items(), samp_fdefs.items()):
            fdef_comp.append(ziplist_stats(v1, v2))
        return fdef_comp

    def compare(self):
        self.__sub_analysis["fcomp_overview_stats"] = self.__compare_fdef_stats()
        self.__print_test_stats()
        self.__show_logical_skeletons()
        # if self.__args.get("l"):
        #     self.__display_lprof_stats()
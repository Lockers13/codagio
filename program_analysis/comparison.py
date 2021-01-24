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
    
    def __display_skelprof(self):
        def print_skelprof(fdef_dict, sub=False):
            for k, v in fdef_dict.items():
                cum_time = float(fdef_dict[k]["cum_time"])
                skeleton = fdef_dict[k]["skeleton"]
                print(skeleton[0][0])
                for skel in skeleton[1:]:
                    print("{0} (%time : {1}%) (real time : {2}s)".format(skel[0], skel[1], '%.2E' % ((float(skel[1])/100) * cum_time)))
                if sub:
                    print("\nCorrectness of Output Score = {0}\n".format(self.__sub_analysis["score"]))
            

        samp_fdefs = self.__samp_analysis["fdefs"]
        sub_fdefs = self.__sub_analysis["fdefs"]
        print("Displaying sample skelprof:\n------------------------------------------")
        print_skelprof(samp_fdefs)
        print("\nDisplaying submission skelprof:\n------------------------------------------")
        print_skelprof(sub_fdefs, sub=True)

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
        if self.__args.get("l"):
            self.__display_skelprof()
        return self.__sub_analysis
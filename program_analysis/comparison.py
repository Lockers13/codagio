import json
import os

class Comparer:

    def __init__(self, analyzer):
        self.__filename, self.__simple_basename, self.__data_path = analyzer.get_paths()
        self.__sub_analysis = analyzer.get_prog_dict()
        self.__samp_analysis = self.__get_sample_analysis()

    def __get_sample_analysis(self):
        with open("{0}_analysis.json".format(self.__data_path), 'r') as f:
            samp_analysis = json.loads(f.read())
        return samp_analysis
    
    def __display_skeleton(self):
        samp_fdefs = self.__samp_analysis["fdefs"]
        for k, v in samp_fdefs.items():
            fname = samp_fdefs[k]["name"]
            skeleton = samp_fdefs[k]["skeleton"]
            for line in skeleton:
                print(line)
            print()

    def __compare_fdef_stats(self):
        """

        Returns a list of lists containing pairwise comparison stats.
        """
        def ziplist_stats(sub, samp):
            fdef_comp_stats = []
            for (k1, v1), (k2, v2) in zip(sub.items(), samp.items()):
                if not isinstance(v1, dict) and not isinstance(v2, dict) and (k1 != "skeleton" and k2 != "skeleton"):
                    inner_comp = []
                    inner_comp.append("{0} : {1}".format(k1, v1))
                    inner_comp.append("{0} : {1}".format(k2, v2))
                    fdef_comp_stats.append(inner_comp)
            return fdef_comp_stats

        sub_fdefs, samp_fdefs = self.__sub_analysis["fdefs"], self.__samp_analysis["fdefs"]
        fdef_comp = []
        for (k1, v1), (k2, v2) in zip(sub_fdefs.items(), samp_fdefs.items()):
            fdef_comp.append(ziplist_stats(v1, v2))
        return fdef_comp

    def compare(self):
        self.__sub_analysis["fcomp_overview_stats"] = self.__compare_fdef_stats()
        self.__display_skeleton()
        return self.__sub_analysis
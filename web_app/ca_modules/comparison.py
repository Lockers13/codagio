import json
import os
from . import make_utils

def write_comp(sub, samp):
    def ziplist_stats(sub, samp):
        fdef_comp_stats = []
        new_sub = make_utils.json_reorder(sub)
        for (k1, v1), (k2, v2) in zip(new_sub.items(), samp.items()):
            if not isinstance(v1, dict):
                inner_comp = []
                sub_stats = "{0} : {1}".format(k1, v1)
                sample_stats = "{0} : {1}".format(k2, v2)
                inner_comp.append(sub_stats)
                inner_comp.append(sample_stats)
                fdef_comp_stats.append(inner_comp)
        return fdef_comp_stats, samp["skeleton"]

    fdef_comp = []
    samp_skels = []
    sub_fdefs, samp_fdefs = sub["fdefs"], samp["fdefs"]
    new_sub_fdefs = make_utils.json_reorder(sub_fdefs)
    for (k1, v1), (k2, v2) in zip(new_sub_fdefs.items(), samp_fdefs.items()):
        fcomp_stats, samp_skel = ziplist_stats(v1, v2)
        fdef_comp.append(fcomp_stats)
        samp_skels.append(samp_skel)
    
    sub["comp_stats"] = fdef_comp
    sub["samp_skels"] = samp_skels

    i = 0
    for imp in samp["imports"]:
        sub["samp_skels"].insert(i, [imp])
        i += 1
    # sub["samp_skels"].insert(i, ["\n"])
    
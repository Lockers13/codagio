#!/usr/bin/env python
# coding: utf-8

# In[33]:


import json
import os


# In[34]:


def get_analyses(s_name):
    analyses = []
    s_type = "submissions"
    for i in range(2):
        s_path = os.path.join(s_type, s_name, s_name)
        with open("{0}_analysis.json".format(s_path), 'r') as f:
            analyses.append(json.loads(f.read()))
            s_type = "sample_problems"
    return analyses[0], analyses[1]


# In[35]:


sub_analysis, samp_analysis = get_analyses("prime_checker")


# In[36]:


def rprint_dict(nested, indent=0):
    """Helper function to recursively print nested dicts.

    Returns None"""

    for k, v in nested.items():
        if isinstance(v, dict):
            print("{0}{1}:".format("    " * indent, k))
            rprint_dict(v, indent+1)
        else:
            print("{0}{1}: {2}".format("    " * indent, k, v))


# In[88]:


def compare_analyses(sub, samp):
    def get_fdefs(analysis):
        stock_functions = ["main", "prep_input"]
        fdefs = analysis['fdefs']
        fdef_keys = list(fdefs.keys())
        for key in fdef_keys:
            if fdefs[key]['name'] in stock_functions:
                fdefs.pop(key, None)
        return fdefs

    def print_func_stats_parallel(sub, samp):
        print("Submission\t|\tSample\n-----------------------------------")
        for key1, key2 in zip(sub.keys(), samp.keys()):
            if not isinstance (sub[key1], dict) and not isinstance (samp[key2], dict):
                print("{0} : {1} | {2} : {3}".format(key1, sub[key1], key2, samp[key2]))
        
    fdefs_sub, fdefs_samp = get_fdefs(sub), get_fdefs(samp)
    fdefs_sub_keys, fdefs_samp_keys = fdefs_sub.keys(), fdefs_samp.keys()
    
    for fkey in fdefs_sub_keys:
        print_func_stats_parallel(fdefs_sub[fkey], fdefs_samp[fkey])
        


# In[89]:


compare_analyses(sub_analysis, samp_analysis)


# In[ ]:





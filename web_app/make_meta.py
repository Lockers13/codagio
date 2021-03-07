import os
import json

meta = {}

meta["diffictuly"] = "Medium"
meta["description"] = "Rot13 Cypher"
meta["constraints"] = {}
constraints = meta["constraints"]

constraints["num_args"] = 1
constraints["allowed_abs_imports"] = ["string"]
constraints["allowed_rel_imports"] = {"string": ["ascii_letters"]}
constraints["disallowed_functions"] = ["eval", "print", "sorted"]

with open(os.path.join("sample_problems", "rot13_meta.json"), 'w') as f:
    f.write(json.dumps(meta))
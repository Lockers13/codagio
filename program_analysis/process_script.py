import argparse
import sys
import os
from analyzer import Analyzer

# example submission call : python process_script.py -s prime_checker -t submission -l
# example sample call : python process_script.py -s quicksort -t sample -l

def parse_clargs():
    """Helper function to parse command line args.

    Returns arg dict"""

    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--script", type=str, required=True,
                help="name of script to be analyzed")
    ap.add_argument("-t", "--type", type=str, required=True,
                help="submission or sample") 
    ap.add_argument("-g", action="store_true")
    ap.add_argument("-l", action="store_true")
    return vars(ap.parse_args())

def main():
    args = parse_clargs()
    upload_type = "submissions" if args.get("type") == "submission" else "sample_problems" if args.get("type") == "sample" else None

    if upload_type is None:
        sys.exit(1)

    # script to be analyzed
    try:
        filename = os.path.join(upload_type, args.get("script"), "{0}.py".format(args.get("script")))  
    except:
        print("Error: incorrect clargs!")
        sys.exit(1)

    analyzer = Analyzer(filename, args)
    analyzer.visit_ast()
    analyzer.verify()
    analyzer.profile()
    if args.get("type") == "submission":
        analyzer.compare()
    analyzer.write_to_json()
    #analyzer.rprint_dict(analyzer.get_prog_dict())

if __name__ == "__main__":
    main()
import hashlib 
import subprocess

class Verifier:
    
    def __init__(self, filename):
        self.__filename = filename
        self.__sample_hash = self.__get_sample_hash()

    def __make_output_hash(self):
        try:
            process = subprocess.Popen(["python", "{0}".format(self.__filename)], stdout=subprocess.PIPE)
        except Exception as e:
            print("Exception in verify_output:", str(e))
             
        output = process.stdout.read()
        stripped_sub = output.decode("utf-8").replace('\n', '').replace(' ', '')

        return hashlib.md5(stripped_sub.encode()).hexdigest()

    def __get_sample_hash(self):
        hash_filename = "{0}_hash.txt".format(self.__filename.split(".")[0])
        with open(hash_filename, 'r') as hf:
            sample_hash = hf.read()
        return sample_hash

    def verify_output(self):
        sub_hash = self.__make_output_hash()
        return sub_hash == self.__sample_hash

# vfy = Verifier('quicksort.py')

# print(vfy.verify_output())

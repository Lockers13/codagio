import hashlib

def crack_passwords(hashfile, pword_data):
    check_list = []

    hash_set = set()
    with open(hashfile, 'r') as f:
        for line in f:
            hash_set.add(line.strip('\n'))
    
    for pword in pword_data:
        pword_hash = hashlib.md5(pword.encode('utf8')).hexdigest()
        check_list.append("{0} {1}".format(pword, pword_hash in hash_set))
    
    return check_list
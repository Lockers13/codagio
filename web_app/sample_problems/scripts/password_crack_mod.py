import hashlib

def crack_passwords(pword_list, hashes):
    hashes = set(hashes)
    return [x for x in pword_list if isinstance(x, str) if hashlib.md5(x.encode('utf-8')).hexdigest() in hashes]
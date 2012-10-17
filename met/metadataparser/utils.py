import hashlib


def compare_filecontents(a, b):
    md5_a = hashlib.md5(a).hexdigest()
    md5_b = hashlib.md5(b).hexdigest()
    return (md5_a == md5_b)

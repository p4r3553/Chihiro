import re

def extract_ascii_strings(data, min_len=4):
    return re.findall(rb'[\x20-\x7E]{%d,}' % min_len, data)

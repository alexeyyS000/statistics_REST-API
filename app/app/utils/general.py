import re


def check_string(string, patterns):
    for pattern in patterns:
        if re.match(pattern, string):
            return True
    return False

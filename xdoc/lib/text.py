import re


def utf8str(s):
    return s.encode('utf8') if s else s


def undent(string):
    lines = string.strip().split('\n')
    # first line doesn't really count
    indents = [len(re.match(r'\s*', line).group(0)) for line in lines[1:] if line]
    indent = min(indents)
    return '\n'.join(lines[:1] + [line[indent:] for line in lines[1:]])

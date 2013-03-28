# -*- coding: utf-8 -*-
# MIT Licensed, (c) 2011 Christopher Brown
import re
# from characters import char_syms, char_subs, string_subs
from StringIO import StringIO
# from bib import *    # BibItem


def undent(string):
    lines = string.strip().split('\n')
    indents = [len(re.match(r'\s*', line).group(0)) for line in lines[1:] if line]
    indent = min(indents)
    return '\n'.join(lines[:1] + [line[indent:] for line in lines[1:]])


def pipeUTF(ascii):
    return StringIO(ascii.read().decode('utf-8'))

# -*- coding: utf-8 -*-
import re


def quotes(tex_string):
    # fix quotes for reasonably-sized strings
    tex_string = re.sub(r'"(.{1,200}?)"', r"``\1''", tex_string)
    tex_string = re.sub(r"(\s)'(\S[^']{1,100}\S)'([.,?;\s])", r"\1`\2'\3", tex_string)

    return tex_string


def sections(tex_string):
    # replace §1.1 with \ref{sec:1.1}
    tex_string = re.sub(r'§+(\d+\.?\d*\.?\d*\.?\d*\.?)', r"\\ref{sec:\1}", tex_string)

    return tex_string


def ascii_symbols(tex_string):
    return tex_string.replace(u'==>', u'⇒')


def references(tex_string):
    # replace (14b) with (\ref{14b})
    return re.sub(r'\((\d{1,2}[a-j]?)\)', r"(\\ref{ex:\1})", tex_string)


def spaces(tex_string):
    # collapse spans of double spaces to just one (not that it matters in tex, but it looks cleaner)
    return re.sub('[ ]{2,}', ' ', tex_string)

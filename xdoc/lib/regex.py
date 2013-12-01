def named(name, pattern):
    return '(?P<%s>%s)' % (name, pattern)


def maybe(pattern):
    return '(' + pattern + ')?'


anything = r'.*?'
some = r'.+?'
s = r'\s*'
space = r'\s+'
sep = r'[.?!]'
end = s + '$' + s

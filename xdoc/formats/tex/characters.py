# -*- coding: utf-8 -*-

# a useful reference for many of the different types of accents
# http://en.wikibooks.org/wiki/LaTeX/Special_Characters#Escaped_codes
escape_pairs = [
    (u'\\', r'\backslash{}'),
    (u'{', r'\{'),
    (u'}', r'\}'),  # these need to be first!
    (u'$', r'\$'),
    (u'#', r'\#'),

    # acute
    (u'á', r'\'a'),
    (u'é', r'\'e'),
    (u'í', r'\'i'),
    (u'ó', r'\'o'),
    (u'ú', r'\'u'),
    # double acute
    (u'ő', r'\H{o}'),
    (u'ű', r'\H{u}'),
    # grave
    (u'ò', r'\`{o}'),
    # umlaut
    (u'ö', r'\"o'),
    (u'ü', r'\"u'),
    # circumflex
    (u'ô', r'\^{o}'),
    # breve
    (u'ŏ', r'\u{o}'),
    # caron / hacek (little v)
    (u'č', r'\v{c}'),

    (u'ø', r'\o'),
    (u'Ø', r'\O'),

    (u'∧', r'$\wedge$'),
    (u'∨', r'$\vee$'),
    (u'∀', r'$\forall$'),
    (u'', r'$\forall$'),
    (u'∃', r'$\exists$'),
    (u'', r'$\exists$'),

    (u'¬', r'$\neg$'),
    (u'≠', r'$\neq$'),
    (u'≤', r'$\leq$'),
    (u'', '$<$'),

    (u'∈', r'$\in$'),
    (u'', r'$\in$'),
    (u'∅', r'$\emptyset$'),
    (u'ø', r'$\emptyset$'),
    (u'', r'$\cap$'),

    (u'‘', r'`'),
    (u'’', r"'"),
    (u'“', r'``'),
    (u'”', r"''"),

    (u'…', r'\dots{}'),
    (u'ι', r'$\iota$'),
    (u'λ', r'$\lambda$'),
    (u'', r'$\lambda$'),
    (u'δ', r'$\delta$'),
    (u'ε', r'$\epsilon$'),
    (u'ϕ', r'$\theta$'),
    (u'Π', r'$\Pi$'),
    (u'π', r'$\pi$'),
    (u'θ', r'$\theta$'),
    (u'ϕ', r'$\phi$'),
    (u'', r'$\phi$'),
    (u'α', r'$\alpha$'),
    (u'', r'$\alpha$'),
    (u'β', r'$\beta$'),
    (u'', r'$\beta$'),
    (u'', r' '),
    (u'', r'$\pi$'),
    (u'', r','),

    (u'◊', r'$\lozenge$'),

    (u'\t', r'\hspace{4em}'),
    (u'⇐', r'$\Leftarrow$'),
    (u'⇔', r'$\Leftrightarrow$'),
    (u'⇒', r'$\Rightarrow$'),
    (u'→', r'$\to$'),

    (u'&', r'\&'),
    (u'—', r'---'),  # m-dash
    (u'–', r'--'),  # n-dash
    (u'∞', r'$\infty$'),  # n-dash
    (u'☐', r'$\square$'),
    (u'\xa0', r'\ '),  # non-breaking space

    (u'', r'\{'),
    (u'', r'|'),
    (u'', r'$>$'),
    (u'%', r'\%'),
]
escape_translations = dict((ord(raw), unicode(tex)) for raw, tex in escape_pairs)


def escape(string):
    return string.translate(escape_translations)

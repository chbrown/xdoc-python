# -*- coding: utf-8 -*-
# MIT Licensed, (c) 2011 Christopher Brown

char_map = [
    (u'\\', r'\backslash{}'),
    (u'{', r'\{'),
    (u'}', r'\}'),  # these need to be first!
    (u'$', r'\$'),

    (u"á", r"\'a"),
    (u"é", r"\'e"),
    (u"í", r"\'i"),
    (u"ó", r"\'o"),
    (u"ú", r"\'u"),
    (u"ö", r"\"o"),
    (u"ü", r"\"u"),
    (u"Ø", r'\O'),

    # double acute
    (u"ő", r'\H{o}'),
    (u"ű", r'\H{u}'),

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

    (u"\t", r"\t"),
    (u'⇔', r'$\Leftrightarrow$'),
    (u'→', r'$\to$'),

    (u'&', r'\&'),
    (u'—', r'---'),  # m-dash
    (u'–', r'--'),  # n-dash
    (u'∞', r'$\infty$'),  # n-dash
    (u'☐', r'$\square$'),

    (u'', r'\{'),
    (u'', r'|'),
    (u'', r'$>$'),
    (u'%', r'\%'),
]
char_translations = dict((ord(raw), unicode(tex)) for raw, tex in char_map)

symbols = [
    ('F022', r'$\forall$'),
    ('F023', r'\#'),
    ('F024', r'$\exists$'),
    ('F0CE', r'$\in$'),
    ('F0B9', r'$\neq$'),
    ('F0D8', r'$\neg$'),
    ('F06A', r'$\phi$'),
    ('F050', r'$\Pi$'),
    ('F0D9', r'$\wedge$'),
    ('F0CB', r'$\nsubseteq$'),
    ('F0CD', r'$\subseteq$'),
    ('F0CA', r'$\superseteq$'),
    ('F0E0', r'$\to$'),
    ('F0DA', r'$\vee$'),
    ('F0A7', r'\textsection{}'),
    ('F0A3', r'$\leq$'),
    ('F0DE', r'$\Rightarrow$'),
    ('F0DB', r'$\Leftrightarrow$'),
    ('F0C6', r'$\emptyset$'),
    ('F0C8', r'$\cup$'),
    ('F0C7', r'$\cap$'),
    ('F0CF', r'$\nin$'),
    ('F0BB', r'$\approx$'),
]
symbols_lookup = dict((k, v) for k, v in symbols)

string_substitutions = [
    (u'==>', r'$\Rightarrow$'),
]

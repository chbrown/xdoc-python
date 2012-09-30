# -*- coding: utf-8 -*-
# MIT Licensed, (c) 2011 Christopher Brown

char_subs = [
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

  (u'‘', '`'),
  (u'’', "'"),
  (u'“', '``'),
  (u'”', "''"),

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
  (u'', ' '),
  (u'', r'$\pi$'),
  (u'', ','),

  (u'◊', '$\lozenge$'),

  (u"\t", r"\t"),
  (u'⇔', r'$\Leftrightarrow$'),
  (u'→', r'$\to$'),

  (u'&', r'\&'),
  (u'—', '---'),  # m-dash
  (u'–', '--'),  # n-dash
  (u'∞', r'$\infty$'),  # n-dash
  (u'☐', r'$\square$'),

  (u'', r'\{'),
  (u'', '|'),
  (u'', '$>$'),
  (u'%', r'\%'),
]
char_subs = dict((ord(raw), unicode(tex)) for raw, tex in char_subs)

string_subs = [
  (u'==>', r'$\Rightarrow$'),
]

char_syms = [
  ('F022', '$\forall$'),
  ('F024', '$\exists$'),
  ('F0CE', '$\in$'),
  ('F0B9', '$\neq$'),
  ('F0D8', '$\neg$'),
  ('F06A', '$\phi$'),
  ('F050', '$\Pi$'),
  ('F0D9', '$\wedge$'),
  ('F0CB', '$\nsubseteq$'),
  ('F0CD', '$\subseteq$'),
  ('F0CA', '$\superseteq$'),
  ('F0E0', '$\to$'),
  ('F0DA', '$\vee$'),
  ('F0A7', '\textsection{}'),
  ('F0A3', '$\leq$'),
  ('F0DE', '$\Rightarrow$'),
  ('F0DB', '$\Leftrightarrow$'),
  ('F0C6', '$\emptyset$'),
  ('F0C8', '$\cup$'),
  ('F0C7', '$\cap$'),
  ('F0CF', '$\nin$'),
]

# MIT Licensed, (c) 2011 Christopher Brown

ACCENT_REPLACEMENTS = [
  ['\\', '\backslash{}'],
  ['{', '\{'],
  ['}', '\}'], # these need to be first!

  ["á", "\\\\'a"],
  ["é", "\\\\'e"],
  ["í", "\\\\'i"],
  ["ó", "\\\\'o"],
  ["ú", "\\\\'u"],
  ["ö", "\\\\\"o"],
  ["ü", "\\\\\"u"],
  ["Ø", '\O'],

  ['∧', '$\wedge$'],
  ['∨', '$\vee$'],
  ['∀', '$\forall$'],
  ['', '$\forall$'],
  ['∃', '$\exists$'],
  ['', '$\exists$'],

  ['¬', '$\neg$'],
  ['≠', '$\neq$'],
  ['≤', '$\leq$'],
  ['', '$<$'],

  ['∈', '$\in$'],
  ['', '$\in$'],
  ['∅', '$\emptyset$'],
  ['ø', '$\emptyset$'],
  ['', '$\cap$'],

  ['‘', '`'],
  ['’', "'"],
  ['“', '``'],
  ['”', "''"],

  ['…', '\dots{}'],
  ['ι', '$\iota$'],
  ['λ', '$\lambda$'],
  ['', '$\lambda$'],
  ['δ', '$\delta$'],
  ['ε', '$\epsilon$'],
  ['ϕ', '$\theta$'],
  ['Π', '$\Pi$'],
  ['θ', '$\theta$'],
  ['ϕ', '$\phi$'],
  ['', '$\phi$'],
  ['α', '$\alpha$'],
  ['', '$\alpha$'],
  ['β', '$\beta$'],
  ['', '$\beta$'],
  ['', ' '],
  ['', '$\pi$'],
  ['', ','],

  ['◊', '$\lozenge$'],

  ["\t", "\\t"],
  ['==>', '$\Rightarrow$'],
  ['⇔', '$\Leftrightarrow$'],

  ['&', '\&'],
  ['—', '---'], # m-dash
  ['–', '--'], # n-dash
  ['∞', '$\infty$'], # n-dash
  ['☐', '$\square$'],

  ['', '\{'],
  ['', '|'],
  ['', '$>$'],
  ['%', '\%'],
  ['  ', ' '],
]

CHAR_SYMS = {
  'F022' => '$\forall$',
  'F024' => '$\exists$',
  'F0CE' => '$\in$',
  'F0B9' => '$\neq$',
  'F0D8' => '$\neg$',
  'F06A' => '$\phi$',
  'F050' => '$\Pi$',
  'F0D9' => '$\wedge$',
  'F0CB' => '$\nsubseteq$',
  'F0CD' => '$\subseteq$',
  'F0CA' => '$\superseteq$',
  'F0E0' => '$\to$',
  'F0DA' => '$\vee$',
  'F0A7' => '\textsection{}',
  'F0A3' => '$\leq$',
  'F0DE' => '$\Rightarrow$',
  'F0DB' => '$\Leftrightarrow$',
  'F0C6' => '$\emptyset$',
  'F0C8' => '$\cup$',
  'F0C7' => '$\cap$',
  'F0CF' => '$\nin$',
}

## xdoc

Steps to bootstrap the TeX-ification of Microsoft Word documents:

1. Install from source (best option, at the moment):

        git clone git://github.com/chbrown/docx-tex.git
        cd docx-tex
        python setup.py install

  You should have the main CLI script, `xdoc`, on your `PATH`.

2. Use Word to convert from .doc to .docx, if the document is not already a .docx.
3. To run it, go and find your docx file.

        xdoc original.docx converted.tex

4. As required, the script may also output a `converted.bib` in the same location as `converted.tex`.


## Results:

It's rough, and still needs a lot of work, but it's better than copy & pasting.

The output presumes that `natbib` and `amssym` and friends are within reach.


## Development

### TODO:

* Shrink whitespace out of spans (non-greedy)
  - E.g., `\emph{framework }that we` should be `\emph{framework} that we`
* Cannot have math environments inside a naked sub/superscript.
* Handle styles in footnotes without breaking the footnote due to unstyled whitespace
* Read tabs that are surrounded by text at least as single spaces.


## License

Copyright (c) 2011-2013 Christopher Brown. [MIT Licensed](LICENSE).


## Acknowledgements

Developed while typesetting for [Semantics and Pragmatics](http://semprag.org/) (http://semprag.org/).

## docx2tex

Steps to bootstrap the TeX-ification of Microsoft Word documents:

1. Use Word to convert from .doc to .docx, if the document is not already a .docx.
2. Install `pip`, if you don't have it already:

        easy_install pip

3. And then install directly from the repository:

        pip install -e git://github.com/chbrown/docx-tex.git#egg=docxtex

4. Or install from source:

        git clone git://github.com/chbrown/docx-tex.git
        cd docx-tex
        python setup.py install

5. Cool. It should be installed, so you should have the main script, `docx2tex`, on your `PATH`.
6. To run it, go and find your docx file.

        docx2tex original.docx

7. The script will output to `original.tex` and `original.bib` in the same file.


## Results:

It's rough, and still needs a lot of work, but it's better than copy & pasting.

The output presumes that `natbib` and `amssym` and friends are within reach.


## Dependencies:

    pip install lxml


## License

Copyright (c) 2011-2013 Christopher Brown. [MIT Licensed](LICENSE).


## Acknowledgements

Developed while typesetting for [Semantics and Pragmatics](http://semprag.org/) (http://semprag.org/).

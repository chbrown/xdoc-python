# -*- coding: utf-8 -*-
# MIT Licensed, (c) 2011 Christopher Brown
import argparse
from microsoft import parse_docx


def main():
    #  [-t word.tex] [-b word.bib]
    parser = argparse.ArgumentParser(description='Usage: docx2tex word.docx')
    parser.add_argument('docx', help='Docx file')
    # parser.add_argument('-t', '--tex', type=str, help='TeX output')
    # parser.add_argument('-b', '--bib',  type=str, help='BibTeX output')
    # parser.add_argument('--template', action='store_true')
    args = parser.parse_args()

    tex_path = args.docx.replace('docx', 'tex')  # args.tex or
    bib_path = args.docx.replace('docx', 'bib')  # args.bib or

    print '%s -> %s, %s' % (args.docx, tex_path, bib_path)
    document = parse_docx(args.docx)
    # print document
    # print unicode(document).encode('utf8')

    with open(tex_path, 'w') as tex_fp:
        doc_bytes = unicode(document).encode('utf8')
        print doc_bytes
        tex_fp.write(doc_bytes)
    # with open(bib_path, 'w') as bib_fp:
    #     bib_fp.write(document.bibtex().encode('utf8'))

if __name__ == '__main__':
    main()

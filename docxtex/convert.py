import argparse
from microsoft import parse_docx


def main():
    parser = argparse.ArgumentParser(description='Usage: docx2tex word.docx')
    parser.add_argument('docx', help='Word document file')
    #  [-t word.tex] [-b word.bib]
    # parser.add_argument('-t', '--tex', type=str, help='TeX output')
    # parser.add_argument('-b', '--bib',  type=str, help='BibTeX output')
    # parser.add_argument('--template', action='store_true')
    opts = parser.parse_args()

    tex_path = opts.docx.replace('docx', 'tex')  # opts.tex or
    bib_path = opts.docx.replace('docx', 'bib')  # opts.bib or

    print 'Converting %s -> %s, %s' % (opts.docx, tex_path, bib_path)
    document = parse_docx(opts.docx)

    with open(tex_path, 'w') as tex_fp:
        doc_bytes = document.tex(True, True).encode('utf8')
        print doc_bytes
        tex_fp.write(doc_bytes)
    # with open(bib_path, 'w') as bib_fp:
    #     bib_fp.write(document.bibtex().encode('utf8'))


if __name__ == '__main__':
    main()

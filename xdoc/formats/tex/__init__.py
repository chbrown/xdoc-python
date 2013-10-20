from datetime import datetime
from xdoc.formats.tex.characters import escape
from xdoc.formats.tex import auto
from xdoc.lib import set_diff

import logging
logger = logging.getLogger(__name__)


document_template = r'''\documentclass[10pt]{report}
\usepackage{times}

%% Converted by xdoc on %(timestamp)s

\begin{document}
%(body)s
\end{document}
'''

simple_commands = {
    'italic': r'\emph',
    'bold': r'\textbf',
    'footnote': r'\footnote',
    # lazily make endnotes into footnotes
    'endnote': r'\footnote',
    'superscript': '^',
    'subscript': '_',
}


def serialize_document(document):
    '''
    Converts the spans in a document into a bunch of strings

    yields plain bytestrings (or at least unicode that is totally ascii)
    '''
    # counters = dict()
    # current_styles tracks what styles are currently applied
    current_styles = set()
    for span in document.spans:
        logger.silly('escaping: %r', span.text)

        pop_styles, push_styles, current_styles = set_diff(current_styles, span.styles)
        for style in pop_styles:
            yield '}'

        for style in push_styles:
            # handle the more common styles first:
            if style in simple_commands:
                yield simple_commands[style]
            elif style == 'hyperlink':
                yield r'\href{%s}' % span.attrs['url']
            elif style == 'counter':
                yield r'\ex[]'
            else:
                raise NotImplementedError('Unrecognized style: %s (%s)', style, span)

            yield '{'

        # escape the odd characters before yielding the content, which returns ascii
        yield escape(span.text)
    else:
        # close by popping all styles
        for style in current_styles:
            yield '}'


def read(fp):
    raise NotImplementedError('Reading .tex files is not supported')


def write(tex_fp, bib_fp, document):
    tex_string = ''.join(serialize_document(document))

    # quotes, sections, ascii_symbols, references, spaces
    tex_string = auto.quotes(tex_string)
    tex_string = auto.sections(tex_string)
    tex_string = auto.ascii_symbols(tex_string)
    tex_string = auto.references(tex_string)
    tex_string = auto.spaces(tex_string)

    # embed the document body in template
    timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    tex_string = document_template % dict(body=tex_string, timestamp=timestamp)

    logger.debug('Writing %d byte tex document to file: %s', len(tex_string), tex_fp)
    tex_fp.write(tex_string)

    # export the bibliography
    logger.debug('Writing bib document to file: %s', bib_fp)
    for key, item in document.bibliography.items():
        logger.debug('NOT Writing %s -> %s to bibliography', key, item)
        bib_fp.write(item)

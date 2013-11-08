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


def serialize_reference(reference):
    '''
    \\bibitem is what TeX inline bibliographies call each bibliographic entry

    returns a string
    '''
    contents = [reference.key] + ['%s = {%s}' % (field, escape(value)) for field, value in reference.attrs.items()]
    body = ',\n  '.join(contents)
    # author_re = bib_item.lastnames.join(' (?:and|&) ').gsub("\\", "\\\\\\\\")
    # regexes = {
    #     citet:         Regexp.new(author_re + '\s*\((\d{4}\w?,?\s*)+\)'),
    #     posscitet: Regexp.new(author_re + '\'s \s*\((\d{4}\w?,?\s*)+\)'),
    #     citep:         Regexp.new('\(' + author_re + ',?\s*(\d{4}\w?,?\s*)+\)'),
    #     citealt:     Regexp.new(author_re + ',?\s*(\d{4}\w?,?\s*)+')
    # }
    # regexes.each do |key, regex|
    #     @tex = @tex.gsub(regex) do |match|
    #         refs = $1.split(',').map { |year| bib_item.ref_lastnames + ":" + year }.join(',')
    #         "\\#{key}{#{refs}}"
    return u'@%s{%s}' % (reference.medium, body)


def serialize_document(document):
    '''
    Converts the spans in a document into a bunch of strings

    yields plain bytestrings (or at least unicode that is totally ascii)
    '''
    # counters = dict()
    # current_styles tracks what styles are currently applied
    current_styles = set()
    for span in document.spans:
        pop_styles, push_styles, current_styles = set_diff(current_styles, span.styles)
        # logger.debug('popping styles: %r', pop_styles)
        for style in pop_styles:
            yield '}'

        logger.silly('escaping: %r (pop ) (>>', span.text)

        # logger.debug('pushing styles: %r', push_styles)
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

    # embed the document body into our template
    timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    tex_string = document_template % dict(body=tex_string, timestamp=timestamp)

    logger.debug('Writing %d byte tex document to file: %s', len(tex_string), tex_fp)
    tex_fp.write(tex_string)

    # export the bibliography
    logger.debug('Writing bib document to file: %s', bib_fp)
    for reference in document.references:
        logger.debug('Serializing reference: %s', reference)
        bibitem_string = serialize_reference(reference)
        logger.debug('Writing to bibliography: %s', bibitem_string)
        bib_fp.write(bibitem_string)

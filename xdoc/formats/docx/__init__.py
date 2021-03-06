from xdoc.bibliography import crossref_lookup
from xdoc.formats.docx.reader import parse_docx
import itertools

import logging
logger = logging.getLogger(__name__)


def read(docx_fp):
    # returns a xdoc.dom.Document object
    document = parse_docx(docx_fp)
    # is this the best place to normalize? yes, I think so, unless...
    #   is there any reason we may want pre-normalized spans down the line somewhere?
    document.normalize()

    # after normalizing, try to process the bibliography

    # first, find the start of the bibliography definition by looking for
    #    a bold span that contains the word 'References' or 'Bibliography'
    span_iter = iter(document.spans)
    for span in span_iter:
        if 'bold' in span.styles and ('References' in span.text or 'Bibliography' in span.text):
            break

    # document.references = list(read_bibliography(span_iter))

    return document


def read_bibliography(span_iter):
    for is_break, p_spans in itertools.groupby(span_iter, lambda span: 'break' in span.styles):
        if not is_break:
            p_spans = list(p_spans)
            p_text = ''.join(span.text for span in p_spans)
            logger.debug('Parsing reference: %s', p_text)
            references = list(crossref_lookup(p_text))
            if len(references):
                # consider the paragraphs consumed
                for span in p_spans:
                    span.text = u''
                logger.debug('resolved bibliography_p: %s -> %s', p_text, references)
            else:
                logger.debug('could not parse reference string: %s', p_text)

            for reference in references:
                yield reference


def write():
    raise NotImplementedError('Writing .docx files is not supported')

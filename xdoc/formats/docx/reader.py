'''In this module, parse_ functions return things, read_ functions yield things'''
import re
import zipfile
from xdoc.formats.docx.characters import symbol_map
from lxml import etree

from xdoc.document import Document, Span

import logging
logger = logging.getLogger(__name__)


def to_xml(node):
    # from lxml import objectify
    # objectify.deannotate(node, cleanup_namespaces=True)
    # return objectify.dump(node)
    import copy
    orphan = copy.deepcopy(node)
    etree.cleanup_namespaces(orphan)
    return etree.tostring(orphan, pretty_print=True)


w_namespace = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
# w_ helps wrap around the w: namespace, instead of doing a '{%s}name' % w_namespace
w_ = lambda name: etree.QName(w_namespace, name)
# w_id = '{%s}id' % w_namespace
namespaces = dict(w=w_namespace)


class DocxFootnote(Span):
    def __init__(self, note_id, styles):
        self.note_id = note_id
        self.styles = styles

    def __unicode__(self):
        return u'DocxFootnote(%r, styles=%s)' % (self.note_id, self.styles)


class DocxEndnote(Span):
    def __init__(self, note_id, styles):
        self.note_id = note_id
        self.styles = styles

    def __unicode__(self):
        return u'DocxEndnote(%r, styles=%s)' % (self.note_id, self.styles)


def read_styles(xPr):
    # yields strings
    for child in xPr:
        tag = etree.QName(child.tag).localname
        val = child.get(w_('val'))
        # italics (and bold, but with w:b) can be
        #   <w:rPr><w:i/></w:rPr> or <w:rPr><w:i w:val='1' /></w:rPr>
        #   but not <w:rPr><w:i w:val='0'/></w:rPr>
        if tag == 'i' and val != '0':
            yield 'italic'
        elif tag == 'b' and val != '0':
            yield 'bold'
        elif tag == 'vertAlign' and val == 'subscript':
            yield 'subscript'
        elif tag == 'vertAlign' and val == 'superscript':
            yield 'superscript'
        elif tag == 'position' and val == '-4':
            yield 'subscript'
        elif tag == 'position' and val == '6':
            yield 'superscript'
        else:
            logger.silly('Ignoring xPr > %s', tag)


def read_r(r, p_styles, p_attrs):
    '''
    p_styles and p_attrs are mutable state references

    yields Span objects
    '''
    r_styles = set()

    # an <w:r> will generally contain only one interesting element besides rPr,
    #   e.g., text, footnote reference, endnote reference, or a symbol
    #   but we still iterate through them all; more elegant than multiple find()'s
    for child in r:
        child_tag = etree.QName(child.tag).localname
        if child_tag == 'rPr':
            # presumably, the rPr will occur before anything else (it does in all the docx xml I've come across)
            for style in read_styles(child):
                r_styles.add(style)
        elif child_tag == 'footnoteReference':
            # footnotes and endnotes are stored as references to be resolved after reading the entire document
            note_id = child.get(w_('id'))
            logger.silly('r > footnoteReference #%s: %s', note_id, child.attrib)
            yield DocxFootnote(note_id, r_styles | p_styles)
        elif child_tag == 'endnoteReference':
            note_id = child.get(w_('id'))
            logger.silly('r > endnoteReference #%s: %s', note_id, to_xml(child))
            yield DocxEndnote(note_id, r_styles | p_styles)
        elif child_tag == 'sym':
            char = child.get(w_('char'))
            # symbol_map maps from ascii to unicode
            replacement = symbol_map.get(char, 'XXX: MISSING SYMBOL %r' % char)
            logger.debug('Reading sym=%s: "%s"', char, replacement)
            yield Span(replacement, r_styles | p_styles, **p_attrs)
        elif child_tag == 't':
            yield Span(unicode(child.text), r_styles | p_styles, **p_attrs)
        elif child_tag == 'tab':
            logger.debug('Ignoring tab')
            # yield Span('\t', r_styles | p_styles, **p_attrs)
        elif child_tag == 'instrText':
            # hyperlinks look like this:
            # ' HYPERLINK "http://dx.doi.org/10.1018/s11932-003-7165-1" \t "_blank" '
            # references look like this:
            # ' REF _Ref226606793 \r \h '
            # counters look like this:
            # ' LISTNUM  ' or ' LISTNUM Example ' but I think they refer to the same thing
            # I'm not sure what the ' \* MERGEFORMAT ' instructions are for
            logger.debug('Processing r > instrText: %s', to_xml(child))

            hyperlink_match = re.match(r' HYPERLINK "(.+)" \\t ".+"', child.text)
            if hyperlink_match:
                p_attrs['url'] = hyperlink_match.group(1)
                p_styles.add('hyperlink')

            ref_match = re.match(r' REF (.+)', child.text)
            if ref_match:
                ref = ref_match.group(1)
                logger.debug('Ignoring REF-type r > instrText: %s', ref)
                # prototype = Hyperlink('REF => %s' % ref, r_styles)

            counter_match = re.match(' LISTNUM (.*) $', child.text)
            if counter_match:
                p_attrs['series'] = counter_match.group(1)
                p_styles.add('counter')
        elif child_tag == 'fldChar':
            field_signal = child.get(w_('fldCharType'))
            if field_signal == 'begin':
                logger.silly('Detected fldCharType=begin')
            elif field_signal == 'separate':
                logger.silly('Ignoring fldCharType=separate')
            elif field_signal == 'end':
                change = child.find('{*}numberingChange')
                print 'numberingChange', change
                if change is not None:
                    original = change.get(w_('original'))
                    yield Span(unicode(original), r_styles | p_styles, **p_attrs)
                logger.debug('Found fldCharType=end; reverting p_styles and p_attrs')
                p_styles.clear()
                p_attrs.clear()
            else:
                raise NotImplementedError('Unrecognized fldCharType: %s (%s)', field_signal, to_xml(child))
        else:
            logger.debug('Ignoring r > %s: %s', child_tag, to_xml(child))


def read_p(p):
    # yields Span objects
    p_styles = set()
    p_attrs = dict()

    # we need to read w:p's children in a loop, because each w:p's is not a constituent
    for p_child in p:
        p_child_tag = etree.QName(p_child.tag).localname

        if p_child_tag == 'pPr':
            for style in read_styles(p_child):
                p_styles.add(style)
        elif p_child_tag == 'r':
            for span in read_r(p_child, p_styles, p_attrs):
                yield span
        elif p_child_tag == 'hyperlink':
            # hyperlinks are just wrappers around a single w:r that contains a w:t.
            # you can use the w:hyperlink[@r:id] value and _rels/document.xml.rels to resolve it,
            # but for now I just print the raw link.
            for hyperlink_child in p_child:
                for span in read_r(hyperlink_child, p_styles, p_attrs):
                    yield span
        else:
            logger.debug('Ignoring p > %s: %s', p_child_tag, to_xml(p_child))


def read_docx_notes(notes_fp, notes_path):
    # yields (id: str, [Span]) tuples
    root = etree.parse(notes_fp)
    for note in root.iterfind(notes_path):
        note_id = note.get(w_('id'))
        spans = [span for p in note.iterfind('{*}p') for span in read_p(p)]
        logger.debug('Reading *note: %s=%s', note_id, spans)
        yield note_id, spans


def read_docx_document(document_fp):
    # yields Span objects
    root = etree.parse(document_fp)
    for body in root.iterfind('//{*}body'):
        for p in body.iterfind('{*}p'):
            # Do we really want this spacer? or just more structure inside the document?
            yield Span(u'\n', set())

            for span in read_p(p):
                yield span

            yield Span(u'\n', set())


def parse_docx(docx_fp):
    # returns a Document object
    docx = zipfile.ZipFile(docx_fp, 'r')

    footnotes_fp = docx.open('word/footnotes.xml')
    footnotes = dict(read_docx_notes(footnotes_fp, '{*}footnote'))
    logger.silly('Read footnotes: %s', footnotes)

    endnotes_fp = docx.open('word/endnotes.xml')
    endnotes = dict(read_docx_notes(endnotes_fp, '{*}endnote'))
    logger.silly('Read endnotes: %s', endnotes)

    document_fp = docx.open('word/document.xml')

    def read_docx_document_merged():
        for span in read_docx_document(document_fp):
            logger.debug('Reading span > %s', span)
            # interpolate footnotes and endnotes as a sort of postprocessing step here
            if isinstance(span, DocxFootnote):
                logger.debug('Resolving reference to footnote=%s', span.note_id)
                for note_span in footnotes[span.note_id]:
                    yield Span(note_span.text, note_span.styles | span.styles | set(['footnote']))
            elif isinstance(span, DocxEndnote):
                logger.debug('Resolving reference to endnote=%s', span.note_id)
                for note_span in endnotes[span.note_id]:
                    yield Span(note_span.text, note_span.styles | span.styles | set(['endnote']))
            else:
                yield span

    spans = list(read_docx_document_merged())

    return Document(spans)

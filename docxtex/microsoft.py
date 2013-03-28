# -*- coding: utf-8 -*-
# MIT Licensed, (c) 2011 Christopher Brown
import zipfile
import re
import itertools
from characters import char_translations, symbols_lookup, string_substitutions
from lxml import etree
from . import undent

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = dict(w=w)

tex_commands = dict(
    emph='\\emph{%s}',
    textbf='\\textbf{%s}',
    superscript='^{%s}',
    subscript='_{%s}',
    footnote='\\footnote{%s}'
)


class Text(object):
    def __init__(self, text):
        self.text = unicode(text)

    def __unicode__(self):
        return self.text.translate(char_translations)


class Span(object):
    def __init__(self, children=None, **attrs):
        if not isinstance(children, list):
            raise Exception("Span's construction argument must be a list")
        # hyperlink=None,
        # children can be other spans or just text
        self.children = children or []
        # self.text = text
        # self.hyperlink = hyperlink
        self.attrs = attrs

    def __unicode__(self):
        text = u''.join(map(unicode, self.children))
        print 'text', text
        a, tex, z = re.match(r'^(\s*)(.*?)(\s*)$', text, re.MULTILINE).groups()
        for key, value in self.attrs.items():
            if value:
                tex = tex_commands[key] % tex

        # if self.hyperlink:
            # tex = "\href{%s}{%s}" % (self.hyperlink, tex)

        # add back in the pre and post whitespace
        return u'%s%s%s' % (a, tex, z)

    def stylekey(self):
        keys = ['emph', 'textbf', 'subscript', 'superscript', 'footnote']
        return tuple([self.attrs.get(key, False) for key in keys])  # + [self.hyperlink]

    # def like(self, other):
        # attrs_match = all(self.attrs.get(k) == other.attrs.get(k) for k in self.attrs + other.attrs)
        # return attrs_match and self.hyperlink == other.hyperlink


def collapse_spans(spans):
    # collapses only horizontally
    collapsed = []
    truthy_spans = [span for span in spans if len(span.children) > 0]
    for _, span_iter in itertools.groupby(truthy_spans, lambda s: s.stylekey()):
        spans = list(span_iter)
        all_children = [child for span in spans for child in span.children]
        # text = ''.join(span.text for span in spans)
        # spans[0].hyperlink,
        collapsed.append(Span(all_children, **spans[0].attrs))
    return collapsed

# class SpanSequence(object):
#     # example_counter = 0
#     hyperlink = None

#     def __init__(self):
#         self.spans = []

    # def __unicode__(self):
    #     return u'\n'.join(unicode(span) for span in self.spans)


def parse_r(r, footnotes=None, endnotes=None):
    text = Text(''.join(t.text for t in r.xpath('./w:t', namespaces=NS) if t.text))
    span = Span([text])

    # italics can be <w:rPr><w:i/></w:rPr> or <w:rPr><w:i w:val='1' /></w:rPr> but not <w:rPr><w:i w:val='0'/></w:rPr>
    for i in r.xpath('./w:rPr/w:i', namespaces=NS):
        span.attrs['emph'] = i.get('{%s}id' % w, '1') != '0'

    for b in r.xpath('./w:rPr/w:b', namespaces=NS):
        span.attrs['textbf'] = b.get('{%s}id' % w, '1') != '0'

    if len(r.xpath("./w:rPr/w:vertAlign[@w:val='subscript']", namespaces=NS)):
        span.attrs['subscript'] = True
    if len(r.xpath("./w:rPr/w:position[@w:val='-4']", namespaces=NS)):
        span.attrs['subscript'] = True

    if len(r.xpath("./w:rPr/w:vertAlign[@w:val='superscript']", namespaces=NS)):
        span.attrs['superscript'] = True
    if len(r.xpath("./w:rPr/w:position[@w:val='6']", namespaces=NS)):
        span.attrs['superscript'] = True

    # if self.hyperlink:
        # span.hyperlink = self.hyperlink

    spans = [span]

    # for instrText in r.xpath("./w:instrText", namespaces=NS):
    #     self.hyperlink = re.match('HYPERLINK "(.+)"', instrText.text).group(1)
    # for fldCharType in r.xpath('./w:fldChar/@w:fldCharType', namespaces=NS):
    #     if fldCharType == 'end':
    #         self.hyperlink = None

    # t_node.content.apply_gsubs(accent_replacements)
    # fragments = r_node.find('w:t').map do |t_node|

    for ref in r.xpath('./w:footnoteReference', namespaces=NS):
        note_id = ref.get('{%s}id' % w)
        spans += [Span(footnotes[note_id], footnote=True)]

    for ref in r.xpath('./w:endnoteReference', namespaces=NS):
        note_id = ref.get('{%s}id' % w)
        spans += [Span(endnotes[note_id], footnote=True)]

    for sym in r.xpath('./w:sym', namespaces=NS):
        char = sym.get('char')
        if char in symbols_lookup:
            spans += [Span([symbols_lookup[char]])]
        else:
            spans += [Span(["XXX: WTF MISSING SYMBOL %r" % char])]

    return spans


# def parse_body(body_node, footnotes=None, endnotes=None):
    # span_sequence = SpanSequence()
    # span_sequence.spans.append(Span('------------ BODY -----------'))


def parse_docx(docx_filepath):
    docx_zipfile = zipfile.ZipFile(docx_filepath, 'r')

    def read_notes(zippath, xpath):
        notes = dict()
        notes_fp = docx_zipfile.open(zippath)
        tree = etree.parse(notes_fp)
        for note in tree.xpath(xpath, namespaces=NS):
            note_spans = []
            for r in note.xpath('./w:p/w:r', namespaces=NS):
                note_spans += parse_r(r)
            note_id = note.get('{%s}id' % w)
            notes[note_id] = collapse_spans(note_spans)
        return notes

    footnotes = read_notes('word/footnotes.xml', '//w:footnotes/w:footnote')
    endnotes = read_notes('word/endnotes.xml', '//w:endnotes/w:endnote')

    for note_id, spans in footnotes.items():
        line = 'Footnote #%s: %s' % (note_id, ''.join(map(unicode, spans)))
        logger.debug(line)

    for note_id, spans in endnotes.items():
        line = 'Endnote #%s: %s' % (note_id, ''.join(map(unicode, spans)))
        logger.debug(line)

    spans = []

    doc_fp = docx_zipfile.open('word/document.xml')
    doc_tree = etree.parse(doc_fp)
    for body in doc_tree.xpath('//w:body', namespaces=NS):
        # \n\n is the body separator
        # body_spans = [Span('\n--------------------------\n')]
        for p in body.xpath('./w:p', namespaces=NS):
            spans += [Span([Text('\n')])]
            for r in p.xpath('./w:r', namespaces=NS):
                # interpolate footnotes and endnotes by sending them along here
                spans += parse_r(r, footnotes, endnotes)

    return Document(collapse_spans(spans))


class Document(object):
    # footnotes = None
    # endnotes = None

    def __init__(self, spans):
        self.spans = spans
        self.bibliography = []

            # for r in p.xpath('./w:r', namespaces=NS):
                # self.read_p(p)
            # self.spans += [Span(['\n\n'])]
    # def read_p(self, p):
        # tex += "#{p_span}\n"
        # removed $ from /^\s*References\s*$/
        # @bibliography_mode = /^\s*References\s*/.match(p_span) || /^\s*(\\textbf\{)?Bibliography(\})?:?\s*$/.match(p_span)


    # def tex(self):
    #     return '\n'.join(span.tex() for span in self.spans)

    def __unicode__(self, postprocess=False, template=False):
        latex = u''.join(map(unicode, self.spans))
        if postprocess:
            # fix latex quotes for reasonably-sized strings
            latex = re.sub(r'"(.{1,200}?)"', r"``\1''", latex)
            latex = re.sub(r"(\s)'(\S[^']{1,100}\S)'([.,?;\s])", r"\1`\2\'\3", latex)

            # replace §1.1 with \ref{sec:1.1}
            latex = re.sub(r'§+(\d+\.?\d*\.?\d*\.?\d*\.?)', "\ref{sec:\1}", latex)

            # replace (14b) with (\ref{14b})
            latex = re.sub(r'\((\d{1,2}[a-j]?)\)', r"(\ref{ex:\1})", latex)

            for before, after in string_substitutions:
                latex = latex.replace(before, after)

            latex = re.sub('[ ]{2,}', ' ', latex)

        if template:
            latex = undent(r'''
            \documentclass[10pt]{report}
            \usepackage{times}

            \begin{document}
            %s
            \end{document}''') % latex

        return latex

        # self.interpolate_bibliography()
        # self.collapse()
        # return self
        # self.postprocess()

    # def bibtex(self):
        # return ''

    # def interpolate_bibliography
    #     self.bibliography.each do |bib_item|
    #         author_re = bib_item.lastnames.join(' (?:and|&) ').gsub("\\", "\\\\\\\\")
    #         regexes = {
    #             citet:         Regexp.new(author_re + '\s*\((\d{4}\w?,?\s*)+\)'),
    #             posscitet: Regexp.new(author_re + '\'s \s*\((\d{4}\w?,?\s*)+\)'),
    #             citep:         Regexp.new('\(' + author_re + ',?\s*(\d{4}\w?,?\s*)+\)'),
    #             citealt:     Regexp.new(author_re + ',?\s*(\d{4}\w?,?\s*)+')
    #         }
    #         regexes.each do |key, regex|
    #             @tex = @tex.gsub(regex) do |match|
    #                 refs = $1.split(',').map { |year| bib_item.ref_lastnames + ":" + year }.join(',')
    #                 "\\#{key}{#{refs}}"

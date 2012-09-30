# -*- coding: utf-8 -*-
# MIT Licensed, (c) 2011 Christopher Brown
import argparse
import re
from zipfile import ZipFile
from lxml import etree
from characters import char_syms, char_subs, string_subs
import itertools
from StringIO import StringIO
# from bib import *    # BibItem
namespaces = dict(w="http://schemas.openxmlformats.org/wordprocessingml/2006/main")

def undent(string):
    lines = string.strip().split('\n')
    indents = [len(re.match(r'\s*', line).group(0)) for line in lines[1:] if line]
    indent = min(indents)
    return '\n'.join(lines[:1] + [line[indent:] for line in lines[1:]])

def pipeUTF(ascii):
    return StringIO(ascii.read().decode('utf-8'))

class Span(object):
    emph = False
    textbf = False
    subscript = False
    superscript = False
    hyperlink = None
    footnote = False

    @property
    def keyattrs(self):
        names = ['emph', 'textbf', 'subscript', 'superscript', 'hyperlink', 'footnote']
        return tuple(getattr(self, key) for key in names)

    def __init__(self, fragments=None):
        self.fragments = fragments or []

    def tex(self, ignore_styles=False):
        tex = (u''.join(self.fragments)).translate(char_subs)
        if not ignore_styles:
            pre = re.search(r'^\s+', tex)
            post = re.search(r'\s+$', tex)
            tex = tex.strip()
            if self.emph:
                tex = "\\emph{%s}" % tex
            if self.textbf:
                tex = "\\textbf{%s}" % tex
            if self.superscript:
                tex = "^{%s}" % tex
            if self.subscript:
                tex = "_{%s}" % tex
            if self.footnote:
                tex = '\\footnote{%s}' % tex
            if pre:
                tex = pre.group(0) + tex
            if post:
                tex = tex + post.group(0)
            if self.hyperlink:
                tex = "\href{%s}{%s}" % (self.hyperlink, tex)
        return tex

class SpanSequence(object):
    example_counter = 0
    hyperlink = None

    def __init__(self):
        self.spans = []

    def tex(self, ignore_styles=False):
        return ''.join([span.tex(ignore_styles) for span in self.spans])

    def collapse(self):
        collapsed_spans = []
        span_iter = (span for span in self.spans if len(''.join(span.fragments)) > 0)
        for _, spans in itertools.groupby(span_iter, lambda s: s.keyattrs):
            spans = list(spans)
            s = spans[0]
            s.fragments = [fragment for span in spans for fragment in span.fragments]
            collapsed_spans.append(s)
        self.spans = collapsed_spans

    def read_body(self, body):
        for p in body.xpath('./w:p', namespaces=namespaces):
            # print p.text
            self.read_p(p)
            self.spans += [Span(['\n\n'])]

    def read_p(self, p):
        for r in p.xpath('./w:r', namespaces=namespaces):
            self.read_r(r)

        # tex += "#{p_span}\n"
        # removed $ from /^\s*References\s*$/
        # @bibliography_mode = /^\s*References\s*/.match(p_span) || /^\s*(\\textbf\{)?Bibliography(\})?:?\s*$/.match(p_span)


    def read_r(self, r):
        fragments = [t.text for t in r.xpath('./w:t', namespaces=namespaces)]

        span = Span(fragments)

        for i in r.xpath('./w:rPr/w:i', namespaces=namespaces):
            val = i.xpath('./@w:val', namespaces=namespaces)
            # print "i val", val
            if len(val) == 0 or val[0] != '0':
                span.emph = True

        for b in r.xpath('./w:rPr/w:b', namespaces=namespaces):
            val = b.xpath('./@w:val', namespaces=namespaces)
            # print 'b val', val
            if len(val) == 0 or val[0] != '0':
                span.textbf = True

        for subscript in r.xpath("./w:rPr/w:vertAlign[@w:val='subscript']", namespaces=namespaces):
            span.subscript = True
        for subscript in r.xpath("./w:rPr/w:position[@w:val='-4']", namespaces=namespaces):
            span.subscript = True

        for superscript in r.xpath("./w:rPr/w:vertAlign[@w:val='superscript']", namespaces=namespaces):
            span.superscript = True
        for superscript in r.xpath("./w:rPr/w:position[@w:val='6']", namespaces=namespaces):
            span.superscript = True

        if self.hyperlink:
            span.hyperlink = self.hyperlink

        self.spans.append(span)

        for instrText in r.xpath("./w:instrText", namespaces=namespaces):
            self.hyperlink = re.match('HYPERLINK "(.+)"', instrText.text).group(1)
        for fldCharType in r.xpath('./w:fldChar/@w:fldCharType', namespaces=namespaces):
            if fldCharType == 'end':
                self.hyperlink = None

        # t_node.content.apply_gsubs(accent_replacements)
        # fragments = r_node.find('w:t').map do |t_node|

        for footnoteReference in r.xpath('./w:footnoteReference', namespaces=namespaces):
            note_id = footnoteReference.get('id')
            note = self.footnotes[note_id]
            span = Span([note])
            span.footnote = True
            self.spans.append(span)

        for endnoteReference in r.xpath('./w:endnoteReference', namespaces=namespaces):
            note_id = endnoteReference.get('id')
            note = self.endnotes[note_id]
            span = Span([note])
            span.footnote = True
            self.spans.append(span)

        for sym in r.xpath('./w:sym', namespaces=namespaces):
            char = sym.get['char']
            if char_syms[char]:
                self.spans += [Span([char_syms[char]])]
            else:
                # char.unpack('U').map(&:to_s)
                self.spans += ["XXX: WTF MISSING SYMBOL %r" % char]

class Document(SpanSequence):
    mode = 'body'

    def __init__(self, docx_filepath):
        super(Document, self).__init__()
        self.bibliography = []
        self.footnotes = dict()
        self.endnotes = dict()

        docx_zip = ZipFile(docx_filepath, 'r')
        try:
            xml_doc = docx_zip.read('word/footnotes.xml').decode('utf-8')
            tree = etree.parse(StringIO(xml_doc))
            for note in tree.xpath('//w:footnotes/w:footnote', namespaces=namespaces):
                doc = SpanSequence()
                doc.read_body(note)
                self.footnotes[note.get('id')] = doc.tex()
        except Exception, exc:
            raise

        try:
            xml_doc = docx_zip.read('word/endnotes.xml').decode('utf-8')
            tree = etree.parse(StringIO(xml_doc))
            for note in tree.xpath('//w:endnotes/w:endnote', namespaces=namespaces):
                doc = SpanSequence()
                doc.read_body(note)
                self.endnotes[note.get('id')] = doc.tex()
        except Exception, exc:
            print 'Could not read endnotes: %s' % exc

        xml_doc = docx_zip.read('word/document.xml').decode('utf-8')
        # self.tex = self.read_body()
        document_tree = etree.parse(StringIO(xml_doc))
        # spans = []
        for body in document_tree.xpath('//w:body', namespaces=namespaces):
            self.read_body(body)

        # self.interpolate_bibliography()
        # self.collapse()
        # return self
        # self.postprocess()

    def bibtex(self):
        return ''

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

def postprocess(tex):
    # fix latex quotes for reasonably-sized strings
    tex = re.sub(r'"(.{1,200}?)"', r"``\1''", tex)
    tex = re.sub(r"(\s)'(\S[^']{1,100}\S)'([.,?;\s])", r"\1`\2\'\3", tex)

    # replace §1.1 with \ref{sec:1.1}
    tex = re.sub(r'§+(\d+\.?\d*\.?\d*\.?\d*\.?)', "\ref{sec:\1}", tex)

    # replace (14b) with (\ref{14b})
    tex = re.sub(r'\((\d{1,2}[a-j]?)\)', r"(\ref{ex:\1})", tex)

    for a, z in string_subs:
        tex = tex.replace(a, z)

    tex = re.sub('[ ]{2,}', ' ', tex)

    return tex

def template(tex):
    return undent(r'''
    \documentclass[10pt]{report}
    \usepackage{times}

    \begin{document}
    %s
    \end{document}''') % tex

def main():
    parser = argparse.ArgumentParser(description='Usage: docx2tex word.docx [-t word.tex] [-b word.bib]')
    parser.add_argument('docx', type=str, help='Docx file')
    parser.add_argument('-t', '--tex', type=str, help='TeX output')
    parser.add_argument('-b', '--bib',  type=str, help='BibTeX output')
    parser.add_argument('--template', action='store_true')
    args = parser.parse_args()

    tex_path = args.tex or args.docx.replace('docx', 'tex')
    bib_path = args.bib or args.docx.replace('docx', 'bib')

    print '%s -> %s, %s' % (args.docx, tex_path, bib_path)
    document = Document(args.docx)
    document.collapse()
    tex = document.tex()
    tex = postprocess(tex)
    if args.template:
        tex = template(tex)
    open(tex_path, 'w').write(tex.encode('utf8'))
    open(bib_path, 'w').write(document.bibtex().encode('utf8'))
    # IO.write(options[:bib_filepath], doc.bibliography.map(&:to_s).join(''))

if __name__ == '__main__':
    main()

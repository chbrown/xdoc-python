'''An ad-hoc DOM of sorts'''
import itertools
import copy

from xdoc.lib.base import object_ustr
from xdoc.lib.text import empty


class Document(object_ustr):
    def __init__(self, spans=None, **metadata):
        # metadata is for things like author, title, date, etc.,
        #   that might be printed on each page (in headers/footers)
        self.spans = spans or []
        self.metadata = metadata
        self.bibliography = dict()

    def normalize(self):
        '''
        AKA, collapse, AKA, optimize. Collect sequential spans together as
        possible, smoothing out whitespace to match neighbors.

        It's easiest to modify existing Span objects, so this is done in-place

        * Find groups of contiguous styles (whitespace has flexible styles),
          but de-style whitespace outside such groups.
        * Previously, this would simply have empty or total-whitespace spans
          adopt the styles of the most recent non-whitespace span, but that
          isn't pretty.
        '''
        inner_spans = []
        outer_spans = []
        current_styles = set()
        for span in self.spans:
            if empty(span.text):
                outer_spans.append(span)
            elif span.styles == current_styles:
                # a non-empty span with identical styles triggers:
                # merging outer_spans into inner_spans
                inner_spans += outer_spans
                outer_spans = []
            else:
                # a non-empty span with new styles triggers:
                # 1) applying current_styles to all inner_spans
                for span in inner_spans:
                    span.styles = current_styles
                inner_spans = []
                # 2) erasing all styles from outer_spans
                for span in outer_spans:
                    span.styles = set()
                outer_spans = []
                # 3) setting current_styles
                current_styles = span.styles

        # now that the styles are all sanitized and updated, we can use the standard groupby
        span_group_iter = itertools.groupby(self.spans, lambda span: span.styles)
        self.spans = [Span.merge(span_group) for styles, span_group in span_group_iter]

    def __unicode__(self):
        return u'Document(metadata=%s, bibliography=%s, spans=%s)' % (
            self.metadata, self.bibliography, u''.join(self.spans))


class Span(object_ustr):
    '''
    The primary building block of a Document

    A Hyperlink is just a Span, except that 'hyperlink' should always be an element of its `styles` set,
    and it also has a `url` field that designates the target url (the `text` field is the display text).

    A Counter is also just a Span, but with the required style of 'counter', and a `series` string value,
    which refers to the name of the counter that is incremented and displayed each time a Counter is resolved.
    It has an empty text value.
    '''
    def __init__(self, text, styles, **attrs):
        self.text = text
        self.styles = styles
        self.attrs = copy.deepcopy(attrs)

    def __unicode__(self):
        return u'Span(%r, styles=%s, attrs=%s)' % (self.text, self.styles, self.attrs)

    @classmethod
    def merge(cls, spans):
        first = next(spans)
        spans = itertools.chain([first], spans)
        return cls(''.join(span.text for span in spans), styles=first.styles, **first.attrs)

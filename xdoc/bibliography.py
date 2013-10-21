import re
from xdoc.dom import Author, Reference

import logging
logger = logging.getLogger(__name__)


def named(name, pattern):
    return '\s*(?P<%s>%s)' % (name, pattern)

anything = r'.*?'
some = r'.+?'
s = r'\s*'
sep = r'\.'
year = '\d{4}'

# \((\d{4}\w?,?)+\)/
# re_authors = r'(?P<authors>.+?)\s*'
# re_authors_editors = r'(?P<authors>.+?)\s*(?P<editor>\(ed(itor)?s\.?\)\s+)?\s*'
re_editors = r'(?P<editor>.+?)\s*\(ed(itor)?s?\.?\)\s*'
# re_year = r'\((?P<year>\)\s*'
re_title = r'(?P<title>[^.]+)\.\s*'
re_title_i = r'(?P<title>.+?)[.,]?\s*'
# re_journal = r'(?P<journal>.+?)\.?\s*'
re_page = r'(?P<page_begin>\d+)-(?P<page_end>\d+)'
re_vol = r'((Volume)?\s*(?P<volume>\d+(\.\d+)?):?\s*' + re_page + ')?'
re_pub_address = r'(?P<publisher>[^,]+)([.,]|, (?P<address>.*[^.])[.,]?)\s*'


media_regex = [{
    # Berman, Steve (1991) \emph{On the Semantics and Logical Form of Wh-Clauses}. Ph.D. dissertation, University of Massachusetts at Amherst.
    'medium': 'phdthesis',
    'pattern':
        named('authors', some) + sep +
        named('year', year) + sep +
        named('title', some) + sep +
        anything + 'dissertation,?' +
        named('school', some)
}, {
    # von , Kai (1995) A minimal theory of adverbial quantification. Ms., MIT, Cambridge, MA.
    'medium': 'unpublished',
    'defaults': dict(note=u'Manuscript'),
    'pattern':
        named('authors', some) + sep +
        named('year', year) + sep +
        named('title', some) + sep +
        '(ms|manuscript|unpublished),' + re_pub_address,
}, {
    # Beckman, Mary E., and Janet Pierrehumbert (1986) Intonational structure in Japanese and English. \emph{Phonology Yearbook} 3:15-70.
    'medium': 'article',
    'pattern':
        named('authors', some) + sep +
        named('year', year) + sep +
        named('title', some) + sep +
        named('journal', some) + re_vol

}, {
    # Bratman, Michael E. (1987) \emph{Intentions, Plans, and Practical Reason}. Harvard University Press, Cambridge, MA.
    'medium': 'book',
    'pattern':
        named('authors', some) + sep +
        named('year', year) + sep +
        named('title', some) + sep +
        re_pub_address
}, {
    # B\"uring, Daniel (1994) Topic. In Bosch & van der Sandt (1994), Volume 2: 271-280.
    'medium': '...?',
    'pattern': 'xyzxyzxyz',
}, {
    # Krifka, Manfred (1992) A compositional semantics for multiple focus constructions.  In Joachim Jacobs (ed.) \emph{Informationsstruktur und Grammatik}. Westdeutscher Verlag, Weisbaden, Germany, 17-53.
    # Roberts, Craige (1995b) Anaphora in intensional contexts. In Shalom Lappin (ed.) \emph{Handbook of Semantics}. Blackwell, London.
    'medium': 'inbook',
    'pattern':
        named('authors', some) + sep +
        named('year', year) + sep +
        named('title', some) + sep +
        'In ' +
        named('editors', some) + sep +
        named('booktitle', some) + sep +
        re_pub_address + '(' + re_page + ')?',
}, {
    'medium': 'article',
    'defaults': dict(note=u'FIXME'),
    'pattern':
        named('authors', some) + sep +
        named('year', year) + sep +
        anything +
        named('title', some)
}]


def parse_string(text):
    # given a raw (unformatted) string that contains some number of bibliographic-like entries
    #   parse the fields in each one (and the medium based on the regex that matches)
    # yields Reference objects
    for medium_regex in media_regex:
        logger.silly('Testing regex: %s', medium_regex)
        match = re.match(medium_regex['pattern'], text)

        if match:
            logger.debug('Using medium_regex "%s" to parse reference "%s"', medium_regex, text)
            groups = match.groupdict()

            authors_strings = groups.pop('authors').split(r',?\s*?(?:\band\b|&)')
            authors = [Author.from_string(author) for author in authors_strings]

            last_names = '-'.join(author.last_name.lower() for author in authors)

            attrs = medium_regex.get('defaults', {}).copy()
            attrs['author'] = ' and '.join(map(unicode, authors))

            page_begin, page_end = groups.pop('page_begin', None), groups.pop('page_end', None)
            if page_begin and page_end:
                attrs['pages'] = '%s--%s' % (page_begin, page_end)

            # maybe filter to only the groups that have non-empty values?
            for field, value in groups.items():
                if value:
                    attrs[field] = value

            yield Reference('%s:%s' % (last_names, groups['year']), medium_regex['medium'], **attrs)

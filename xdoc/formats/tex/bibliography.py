import re

from xdoc.formats.tex import escape
from xdoc.lib.base import object_ustr


class Author(object_ustr):
    def __init__(self, first_name, middle_name, last_name):
        # 'Judy von Linseng' should have a last name of 'von Linseng', not 'Linseng'
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name

    @classmethod
    def parse(cls, raw):
        parts = re.split(r',\s*', raw, maxsplit=2)
        # TODO: handle von-type last names
        if len(parts) == 3:
            return cls(parts[2], parts[1], parts[0])
        elif len(parts) == 2:
            return cls(parts[1], None, parts[0])
        else:
            raise Exception('One-part names are not yet handled')

    def __unicode__(self):
        return ' '.join(filter(None, [self.first_name, self.middle_name, self.last_name]))


class BibItem(object_ustr):
    '''\bibitem is what TeX inline bibliographies call each bibliographic entry'''
    def __init__(self, medium, key, **attrs):
        self.medium = medium
        self.key = key
        self.attrs = attrs

    def __unicode__(self):
        contents = [self.key] + ['%s = {%s}' % (key, escape(value)) for key, value in self.attrs.items()]
        body = ',\n  '.join(contents)
        return u'@%s{%s}' % (self.medium, body)


# \((\d{4}\w?,?)+\)/
re_authors = r'(?<authors>.+?)\s*(?<editor>\(ed(itor)?s\.?\)\s+)?\s*'
re_editors = r'(?<editor>.+?)\s*\(ed(itor)?s?\.?\)\s*'
re_year = r'\((?<year>(\d{4}\w?/?)+)\)\s*'
re_title = r'(?<title>[^.]+)\.\s*'
re_title_i = r'\\emph\{(?<title>.+?)\}[.,]?\s*'
re_journal = r'\\emph\{(?<journal>.+?)\}\.?\s*'
re_page = r'(?<page_begin>\d+)-(?<page_end>\d+)'
re_vol = r'((Volume)?\s*(?<volume>\d+(\.\d+)?):?\s*' + re_page + ')?'
re_pub_address = r'(?<publisher>[^,]+)([.,]|, (?<address>.*[^.])[.,]?)\s*'


media_regex = [{
    # Berman, Steve (1991) \emph{On the Semantics and Logical Form of Wh-Clauses}. Ph.D. dissertation, University of Massachusetts at Amherst.
    'medium': 'phdthesis',
    'pattern': re_authors + re_year + re_title_i + 'Ph.D. dissertation, (?<school>.+)\.'
}, {
    # von , Kai (1995) A minimal theory of adverbial quantification. Ms., MIT, Cambridge, MA.
    'medium': 'unpublished',
    'pattern': re_authors + re_year + re_title + 'Ms\., ' + re_pub_address,
    'defaults': dict(note='Manuscript'),
}, {
    # Beckman, Mary E., and Janet Pierrehumbert (1986) Intonational structure in Japanese and English. \emph{Phonology Yearbook} 3:15-70.
    'medium': 'article',
    'pattern': re_authors + re_year + re_title + re_journal + re_vol,
}, {
    # Bratman, Michael E. (1987) \emph{Intentions, Plans, and Practical Reason}. Harvard University Press, Cambridge, MA.
    'medium': 'book',
    'pattern': re_authors + re_year + re_title_i + re_pub_address,
}, {
    # B\"uring, Daniel (1994) Topic. In Bosch & van der Sandt (1994), Volume 2: 271-280.
    'medium': '...?',
    'pattern': 'xyzxyzxyz',
}, {
    # Krifka, Manfred (1992) A compositional semantics for multiple focus constructions.  In Joachim Jacobs (ed.) \emph{Informationsstruktur und Grammatik}. Westdeutscher Verlag, Weisbaden, Germany, 17-53.
    # Roberts, Craige (1995b) Anaphora in intensional contexts. In Shalom Lappin (ed.) \emph{Handbook of Semantics}. Blackwell, London.
    'medium': 'inbook',
    'pattern': re_authors + re_year + re_title + 'In ' + re_editors + re_title_i + re_pub_address + '(' + re_page + ')?',
}, {
    'medium': 'article',
    'pattern': re_authors + re_year + '.*' + '\\emph\{(?<title>.+?)\}' + '.*',
    'defaults': dict(note='FIXME'),
}]


def parse_bib_items(text):
    # given a raw (unformatted) string of bibliographic-like entries
    # parse out the contents and medium of each one
    for medium_regex in media_regex:
        for match in re.finditer(medium_regex['pattern'], text):
            groups = match.groupdict()

            authors_strings = groups.pop('authors').split(r',?\s*?(?:\band\b|&)')
            authors = [Author.parse(author) for author in authors_strings]

            last_names = '-'.join(author.last_name.lowercase() for author in authors)
            key = '%s:%s' % (last_names, groups['year'])

            attrs = medium_regex.get('defaults', {}).copy()
            attrs['author'] = ' and '.join(authors)

            page_begin, page_end = groups.pop('page_begin', None), groups.pop('page_end', None)
            if page_begin and page_end:
                attrs['pages'] = '%s--%s' % (page_begin, page_end)

            # maybe filter to only the groups that have non-empty values?
            attrs.update(groups)

            yield BibItem(medium_regex['medium'], key, **attrs)

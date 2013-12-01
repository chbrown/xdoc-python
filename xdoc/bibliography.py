import re
import requests
from xdoc.dom import Author, Reference
from xdoc.lib.regex import named, maybe, anything, some, s, sep, end
from xdoc.formats.tex.bibliography import parse_bibtex
from unidecode import unidecode

from xdoc.lib.log import logging
logger = logging.getLogger(__name__)


# \((\d{4}\w?,?)+\)/
# re_authors = r'(?P<authors>.+?)\s*'
# re_authors_editors = r'(?P<authors>.+?)\s*(?P<editor>\(ed(itor)?s\.?\)\s+)?\s*'
re_editors = r'(?P<editor>.+?)\s*\(ed(itor)?s?\.?\)\s*'
re_year = named('year', '\d{4}') + named('subyear', r'\w?')
re_title = r'(?P<title>[^.]+)\.\s*'
re_title_i = r'(?P<title>.+?)[.,]?\s*'
# \u2013 is the em-dash
re_page = ur'(?P<page_begin>\d+)(-|--|\u2013)(?P<page_end>\d+)'
# :?\s*' + re_page + '
re_vol = r'(Volume\s+)?(?P<volume>\d+(\.\d+)?)'
re_edition = r'\((?P<edition>\d+)\)'
re_pub_address = r'(?P<publisher>[^,]+)([.,]|, (?P<address>.*[^.])[.,]?)\s*'
re_doi = r'(http://dx.doi.org/(?P<doi>\S+))?'


media_regex = [{
    # Horn, Larry. 1972. On the semantic properties of logical operators in English: UCLA dissertation.
    'medium': 'phdthesis',
    'pattern':
        s + named('authors', some) + sep +
        s + re_year + sep +
        s + named('title', some) + r'[.:]' + s +
        named('school', some) + s + 'dissertation' + sep +
        end
}, {
    # Berman, Steve (1991) \emph{On the Semantics and Logical Form of Wh-Clauses}. Ph.D. dissertation, University of Massachusetts at Amherst.
    'medium': 'phdthesis',
    'pattern':
        s + named('authors', some) + sep +
        s + re_year + sep +
        s + named('title', some) + sep +
        anything + 'dissertation,?' +
        s + named('school', some) + sep +
        end
}, {
    # von , Kai (1995) A minimal theory of adverbial quantification. Ms., MIT, Cambridge, MA.
    'medium': 'unpublished',
    'defaults': dict(note=u'Manuscript'),
    'pattern':
        s + named('authors', some) + sep +
        s + re_year + sep +
        s + named('title', some) + sep +
        '(ms|manuscript|unpublished),' + re_pub_address + sep +
        end
}, {
    # Beckman, Mary E., and Janet Pierrehumbert (1986) Intonational structure in Japanese and English. \emph{Phonology Yearbook} 3:15-70.
    'medium': 'article',
    'pattern':
        s + named('authors', some) + sep +
        s + re_year + sep +
        s + named('title', some) + sep +
        s + named('journal', some) + s + re_vol + maybe(s + re_edition) + sep + s + re_page + sep +
        s + re_doi +
        end
}, {
    # Bratman, Michael E. (1987) \emph{Intentions, Plans, and Practical Reason}. Harvard University Press, Cambridge, MA.
    'medium': 'book',
    'pattern':
        s + named('authors', some) + sep +
        s + re_year + sep +
        s + named('title', some) + sep +
        s + named('publisher', some) + ':' + s + named('address', some) + sep +
        end
}, {
    # B\"uring, Daniel (1994) Topic. In Bosch & van der Sandt (1994), Volume 2: 271-280.
    'medium': '...?',
    'pattern': 'xyzxyzxyz',
}, {
    # Krifka, Manfred (1992) A compositional semantics for multiple focus constructions.  In Joachim Jacobs (ed.) \emph{Informationsstruktur und Grammatik}. Westdeutscher Verlag, Weisbaden, Germany, 17-53.
    # Roberts, Craige (1995b) Anaphora in intensional contexts. In Shalom Lappin (ed.) \emph{Handbook of Semantics}. Blackwell, London.
    'medium': 'inbook',
    'pattern':
        s + named('authors', some) + sep +
        s + re_year + sep +
        s + named('title', some) + sep +
        'In ' +
        s + named('editors', some) + sep +
        s + named('booktitle', some) + sep +
        re_pub_address + '(' + re_page + ')?',
}, {
    'medium': 'article',
    'defaults': dict(note=u'FIXME'),
    'pattern':
        s + named('authors', some) + sep +
        s + re_year + sep +
        maybe(s + named('title', some) + sep) +
        anything +
        maybe(s + re_doi)
}]


def regex_parse_string(text):
    # given a raw (unformatted) string that contains some number of bibliographic-like entries
    #   parse the fields in each one (and the medium based on the regex that matches)
    # yields Reference objects
    for medium_regex in media_regex:
        logger.silly('Testing regex: %s', medium_regex)
        match = re.match(medium_regex['pattern'], text)

        if match:
            logger.debug('Using medium_regex "%s" to parse reference "%s"', medium_regex, text)
            groups = match.groupdict()

            authors_strings = re.split(r'\s*(?:\band\b|&)\s*', groups.pop('authors'))
            authors = [Author.from_string(author) for author in authors_strings]

            last_names = ' '.join(author.last_name.lower() for author in authors)
            last_names = unidecode(last_names).replace(' ', '-')
            name = '%s:%s' % (last_names, groups['year'])
            if 'subyear' in groups:
                name += groups.pop('subyear')

            attrs = medium_regex.get('defaults', {}).copy()
            attrs['author'] = ' and '.join(map(unicode, authors))

            page_begin, page_end = groups.pop('page_begin', None), groups.pop('page_end', None)
            if page_begin and page_end:
                attrs['pages'] = '%s--%s' % (page_begin, page_end)

            # maybe filter to only the groups that have non-empty values?
            for field, value in groups.items():
                if value:
                    attrs[field] = value

            yield Reference(name, medium_regex['medium'], **attrs)


def crossref_lookup(text, minimum_score=0.01):
    import requests_cache
    requests_cache.install_cache('/tmp/crossref_cache')
    # requests_cache.install_cache('/tmp/crossref_cache', backend='redis')
    # See the Crossref labs blog at this link for the general approach:
    #   http://labs.crossref.org/resolving-citations-we-dont-need-no-stinkin-parser/
    # and the api help for documentation:
    #   http://search.labs.crossref.org/help/api

    dois_response = requests.get('http://search.labs.crossref.org/dois', params={
        'q': text,
        'rows': 1,  # results per page
        'page': 1,
        'sort': 'score',
    })
    search_results = dois_response.json()
    for search_result in search_results[:1]:
        # each search_result looks like this:
        # {
        #     "coins": "ctx_ver=Z39.88-2004&amp;rft_id=info%3Adoi%2Fhttp%3A%2F%2Fdx.doi.org%2F10.3765%2Fsp.6.2&amp;rfr_id=info%3Asid%2Fcrossref.org%3Asearch&amp;rft.atitle=Strategic+conversation&amp;rft.jtitle=Semantics+and+Pragmatics&amp;rft.date=2013&amp;rft.volume=6&amp;rft.aufirst=Nicholas&amp;rft.aulast=Asher&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&amp;rft.genre=article&amp;rft.au=Nicholas+Asher&amp;rft.au=+Alex+Lascarides",
        #     "doi": "http://dx.doi.org/10.3765/sp.6.2",
        #     "fullCitation": "Nicholas Asher, Alex Lascarides, 2013, 'Strategic conversation', <i>Semantics and Pragmatics</i>, vol. 6",
        #     "normalizedScore": 100,
        #     "score": 5.295812,
        #     "title": "Strategic conversation",
        #     "year": "2013"
        # },
        if search_result['score'] > minimum_score:
            logger.info('Using top result; score = %.2f.', search_result['score'])
            doi_url = search_result['doi']
            # See http://www.crosscite.org/cn/ for details on content negotiation here
            bibtex_response = requests.get(doi_url, headers={'Accept': 'application/x-bibtex'})
            # for some reason, chardet thinks it's iso-8859-2 = latin2 (european), but just decode with utf-8
            bibtex_response.encoding = 'UTF-8'

            # the returned bibtex looks like this (but without line breaks)
            # @article{Asher_Lascarides_2013, title={Strategic conversation},
            #   volume={6}, url={http://dx.doi.org/10.3765/sp.6.2},
            #   DOI={10.3765/sp.6.2}, journal={Semantics and Pragmatics},
            #   publisher={Semantics and Pragmatics}, year={2013}, month={Aug},
            #   author={Asher, Nicholas and Lascarides, Alex}}
            for reference in parse_bibtex(bibtex_response.text):
                yield reference
        else:
            logger.warn('No result has a score > %.2f', minimum_score)

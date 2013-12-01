import sys
import os
import argparse

from xdoc.lib.log import logging


def translate(parser):
    opts = parser.parse_args()
    logger = logging.getLogger(__name__)

    # read input
    input_root, input_extension = os.path.splitext(opts.input)
    if input_extension == '.docx':
        logger.info('Reading from filepath: %s', opts.input)

        from xdoc.formats.docx import read
        with open(opts.input) as fp:
            document = read(fp)
    else:
        raise NotImplementedError('File extension "%s" not supported as input' % input_extension)

    # write output
    output_root, output_extension = os.path.splitext(opts.output)
    if output_extension == '.tex':
        tex_filepath = output_root + '.tex'
        bib_filepath = output_root + '.bib'
        logger.info('Writing to filepaths: %s & %s', tex_filepath, bib_filepath)

        from xdoc.formats.tex import write
        with open(tex_filepath, 'w') as tex_fp:
            with open(bib_filepath, 'w') as bib_fp:
                write(tex_fp, bib_fp, document)
    else:
        raise NotImplementedError('File extension "%s" not supported as output' % output_extension)


def parsebib(parser):
    opts = parser.parse_args()
    logger = logging.getLogger(__name__)

    from xdoc.bibliography import crossref_lookup
    from xdoc.formats.tex import serialize_reference

    input = sys.stdin if (opts.input == '-') else open(opts.input)
    output = sys.stdout if (opts.output == '-') else open(opts.output)

    for line in input:
        line = line.strip().decode('utf8')
        logger.info('Resolving "%s" via CrossRef API', line)

        for bibitem in crossref_lookup(line):
            print >> output, serialize_reference(bibitem)
            break
        else:
            logger.error('FIXME: could not parse bib item: %s', line)

    # import unicodedata
    # crf = train_crf()
        # if line:
            # strip tex if needed (only simple commands; if there are environments, too bad)
            # line = tex_command.sub(line, 'a\1z')
            # line = re.sub(r'\\[a-z]+\{([^\}]+)\}', r'\1', line)

            # tokens = unidecode(line).split()
            # features = [list(token_features(token)) for token in tokens]
            # labels = crf.predict(features)
            # pairs = zip(tokens, labels)
            # print gloss.gloss(pairs, prefixes=('', Fore.GREEN), postfixes=(Fore.RESET, Fore.RESET), groupsep='\n')

actions = dict(translate=translate, parsebib=parsebib)


def main():
    parser = argparse.ArgumentParser(
        description='Usage: xdoc original.docx converted.tex',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # parser.add_argument('input', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('input', help='input filename')
    # parser.add_argument('output', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('output', help='output filename')
    parser.add_argument('-a', '--action', choices=actions, default='translate', help='xdoc action')
    parser.add_argument('-v', '--verbose', action='store_true', help='Log extra output')
    opts = parser.parse_args()

    logging.root.setLevel(logging.DEBUG if opts.verbose else logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info('Logging with level >= %s (%s)', logging.root.level, logging.getLevelName(logging.root.level))

    actions[opts.action](parser)

    logger.debug('Done')

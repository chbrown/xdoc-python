import os
import argparse
import logging
logging.addLevelName(5, 'SILLY')


class Logger(logging.Logger):
    def silly(self, msg, *args, **kwargs):
        level = logging.getLevelName('SILLY')
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)

    def notset(self, msg, *args, **kwargs):
        level = logging.getLevelName('NOTSET')
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)


def main():
    parser = argparse.ArgumentParser(
        description='Usage: xdoc original.docx converted.tex',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('input', help='Input filename')
    parser.add_argument('output', help='Output filename')
    parser.add_argument('-v', '--verbose', action='store_true', help='Log extra output')
    opts = parser.parse_args()

    # max(map(len, [logging.getLevelName(level) for level in range(0, 60, 10)])) == 8
    level = logging.DEBUG if opts.verbose else logging.INFO
    logging.basicConfig(format='%(levelname)-8s %(asctime)14s (%(name)s): %(message)s', level=level)
    logging.setLoggerClass(Logger)
    logger = logging.getLogger(__name__)
    logger.info('Logging with level >= %s (%s)', logging.root.level, logging.getLevelName(logging.root.level))

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

    logger.debug('Done')

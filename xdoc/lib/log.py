import logging

logging.addLevelName(5, 'SILLY')

# max(map(len, [logging.getLevelName(level) for level in range(0, 60, 10)])) == 8
# %(asctime)14s
logging.basicConfig(format='%(levelname)-8s (%(name)s): %(message)s')


class Logger(logging.Logger):
    def silly(self, msg, *args, **kwargs):
        level = logging.getLevelName('SILLY')
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)

    def notset(self, msg, *args, **kwargs):
        level = logging.getLevelName('NOTSET')
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)


logging.setLoggerClass(Logger)

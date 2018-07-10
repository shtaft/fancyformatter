import logging
import sys

import pygments
import pygments_pprint_sql

from pygments import filters
from pygments import formatters
from pygments import lexers

from . import colors


python_traceback_lexer = lexers.PythonTracebackLexer()
terminal_formatter = formatters.TerminalFormatter()
python_lexer = lexers.PythonLexer()
mysql_lexer = lexers.MySqlLexer()
mysql_lexer.add_filter(filters.KeywordCaseFilter(case='upper'))
mysql_lexer.add_filter(pygments_pprint_sql.SqlFilter())


class FancyFormatter(logging.Formatter):

    LEVELS = {
        'CRITICAL': colors.magenta('CRIT'),
        'DEBUG': colors.blue('DEBUG'),
        'ERROR': colors.red('ERROR'),
        'EVENT': colors.green('EVENT', bold=True),
        'INFO': colors.blue('INFO'),
        'WARNING': colors.red('WARN', bold=True),
    }

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super(FancyFormatter, self).__init__(fmt, datefmt)

        # Enable SQLAlchemy formatting by default
        self._formats = [
            SqlalchemyFormat(),
        ]

        self._default_format = DefaultFormat(fmt)

        #: A mapping of logger names to their Format instances.
        self._cache = {}

    def addFormat(self, format):
        self._formats.append(format)
        self._cache.clear()

    def format(self, record):
        name = record.name

        format = self._cache.get(name)
        if format is None:
            for f in self._formats:
                if f.shouldFormat(name):
                    self._cache[name] = f
                    format = f
                    break
            else:
                format = self._default_format

        try:
            fmt = format.fmt or self._fmt
            message = format.getMessage(record).rstrip()
            display_name = format.getName(name)
        except OutputOverride as e:
            return e.output

        s = fmt % dict(
            record.__dict__,
            name=display_name,
            asctime=colors.green(self.formatTime(record, self.datefmt), bold=1),
            msecs_str=colors.green(',%03d' % record.msecs, bold=1),
            levelname=self.LEVELS.get(record.levelname, record.levelname),
            threadName=colors.yellow(record.threadName, bold=1),
            message='%(message)s',
        )

        if '\n' in message:
            try:
                idx = s.index('%(message)s')
            except IndexError:
                pass
            else:
                message = message.replace(
                    '\n',
                    '\n' + ' ' * len(colors.strip(s[:idx])),
                )

        s %= {'message': message}

        if record.exc_info and not record.exc_text:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != '\n':
                s = s + '\n'
            try:
                exc_text = record.exc_text
            except UnicodeError:
                # Sometimes filenames have non-ASCII chars, which can lead
                # to errors when s is Unicode and record.exc_text is str
                # See issue 8924.
                # We also use replace for when there are multiple
                # encodings, e.g. UTF-8 for the filesystem and latin-1
                # for a script. See issue 13232.
                s = s + record.exc_text.decode(sys.getfilesystemencoding(),
                                               'replace')
            s += pygments.highlight(
                exc_text,
                python_traceback_lexer,
                terminal_formatter,
            )

        return s


class Format(object):
    """
    Custom formatting definition for a logger.
    """

    #: An optional custom format string to use for this log line.
    fmt = None

    def shouldFormat(self, logger_name):
        return False

    def getName(self, name):
        return name

    def getMessage(self, record):
        """
        Generate the formatted message string for insertion into the fmt
        string.
        """
        return record.getMessage()


class DefaultFormat(Format):
    def __init__(self, fmt):
        self.fmt = fmt

    def getName(self, name):
        return colors.cyan(name)

    def shouldFormat(self, logger_name):
        return True


class SqlalchemyFormat(Format):
    def shouldFormat(self, logger_name):
        return logger_name == 'sqlalchemy.engine.base.Engine'

    def getName(self, name):
        return colors.green('sqlalchemy')

    def getMessage(self, record):
        message = record.getMessage()

        if message[:1] == '(':
            # Assume that this is a tuple of bind params
            lexer = python_lexer
        else:
            lexer = mysql_lexer

        return pygments.highlight(message, lexer, terminal_formatter)


class OutputOverride(Exception):
    """
    Raise this from your custom Format to override the formatting
    logic in FancyFormatter and use the given output string instead.
    """
    def __init__(self, output):
        self.output = output

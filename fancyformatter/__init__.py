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

    def __init__(self, fmt=None, datefmt=None):
        super(FancyFormatter, self).__init__(fmt, datefmt)

        # Enable SQLAlchemy formatting by default
        self.formats = {
            SqlalchemyFormat.name: SqlalchemyFormat(),
        }

    def addFormat(self, format):
        self.formats[format.name] = format

    def format(self, record):
        name = record.name
        format = self.formats.get(name)

        if format is None:
            fmt = self._fmt
            message = record.getMessage().rstrip()
            display_name = colors.cyan(name)
        else:
            fmt = format.fmt or self._fmt
            message = format.getMessage(self, record).rstrip()
            display_name = format.display_name

        s = fmt % dict(
            record.__dict__,
            name=display_name,
            asctime=colors.green(self.formatTime(record, self.datefmt), bold=1),
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

    #: The logger name that this format should apply to.
    name = None

    #: How the logger name should be displayed in the log line.
    #: You can override it for brevity or to add color.
    display_name = None

    #: An optional custom format string to use for this log line.
    fmt = None

    def getMessage(self, formatter, record):
        """
        Generate the formatted message string for insertion into the fmt
        string.
        """


class SqlalchemyFormat(Format):
    name = 'sqlalchemy.engine.base.Engine'
    display_name = colors.green('sqlalchemy')

    def getMessage(self, formatter, record):
        message = record.getMessage()

        if message[:1] == '(':
            # Assume that this is a tuple of bind params
            lexer = python_lexer
        else:
            lexer = mysql_lexer

        return pygments.highlight(message, lexer, terminal_formatter)

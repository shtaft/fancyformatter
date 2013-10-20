Fancy Formatter for Python Logging
==================================

FancyFormatter helps make the terminal output of Python ``logging`` more
pleasant to read.

   * Common LogRecord fields are colorized to help them stand out.
   * Exception text is highlighted with Pygments.
   * SQLAlchemy queries are pretty printed and highlighted, and
     bind params for queries are also highlighted.
   * Additional formatting can be plugged in for specific loggers.

Usage
-----

When using ``logging.config.fileConfig``, you can configure this formatter with
a section like this:

::

   [formatter_fancyformatter]
   class = fancyformatter.FancyFormatter
   format = %(asctime)s %(threadName)s %(levelname)s %(name)s %(message)s



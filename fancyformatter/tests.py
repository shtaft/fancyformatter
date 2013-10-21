import cStringIO
import logging
import unittest

import fancyformatter


class FancyFormatterTest(unittest.TestCase):

    def setUp(self):
        self.buffer = cStringIO.StringIO()
        self.logger = logging.getLogger('fancyloggertest')
        self.handler = logging.StreamHandler(self.buffer)
        self.assertEqual(self.logger.handlers, [])
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)

    def test_default_format(self):
        self.handler.formatter = fancyformatter.FancyFormatter(
            '%(asctime)s %(levelname)s [%(name)s] %(message)s',
            'TEST_DATE_FMT',
        )
        self.logger.warn('test!')
        self.assertEqual(self.buffer.getvalue(), ''.join([
            '\x1b[1;32mTEST_DATE_FMT\x1b[0m ',
            '\x1b[1;31mWARN\x1b[0m ',
            '[\x1b[36mfancyloggertest\x1b[0m] ',
            'test!\n',
        ]))

    def test_sqlalchemy_format(self):
        self.handler.formatter = fancyformatter.FancyFormatter(
            '%(asctime)s %(levelname)s [%(name)s] %(message)s',
            'TEST_DATE_FMT',
        )

        # Enable the SQLAlchemy format for our logger.
        class SqlalchemyFormat(fancyformatter.SqlalchemyFormat):
            def shouldFormat(self, logger_name):
                return True
        self.handler.formatter.addFormat(
            SqlalchemyFormat()
        )

        self.logger.info('SELECT users.* FROM users INNER JOIN users_groups ON users.id = users_groups.user_id AND users_groups.group_id = %s')
        self.logger.info('(1L,)')

        self.assertEqual(self.buffer.getvalue(), ''.join([
            '\x1b[1;32mTEST_DATE_FMT\x1b[0m ',
            '\x1b[34mINFO\x1b[0m ',
            '[\x1b[32msqlalchemy\x1b[0m] ',
            '\x1b[34mSELECT\x1b[39;49;00m \x1b[39;49;00musers\x1b[39;49;00m.\x1b[39;49;00m*\x1b[39;49;00m\n                                \x1b[34mFROM\x1b[39;49;00m \x1b[39;49;00musers\x1b[39;49;00m\n                                \x1b[34mINNER\x1b[39;49;00m \x1b[39;49;00m\x1b[34mJOIN\x1b[39;49;00m \x1b[39;49;00musers_groups\x1b[39;49;00m\n                                \x1b[34mON\x1b[39;49;00m \x1b[39;49;00musers\x1b[39;49;00m.\x1b[39;49;00mid\x1b[39;49;00m \x1b[39;49;00m=\x1b[39;49;00m \x1b[39;49;00musers_groups\x1b[39;49;00m.\x1b[39;49;00muser_id\x1b[39;49;00m\n                                \x1b[34mAND\x1b[39;49;00m \x1b[39;49;00musers_groups\x1b[39;49;00m.\x1b[39;49;00mgroup_id\x1b[39;49;00m \x1b[39;49;00m=\x1b[39;49;00m \x1b[39;49;00m%\x1b[39;49;00ms\x1b[39;49;00m\n',
            '\x1b[1;32mTEST_DATE_FMT\x1b[0m ',
            '\x1b[34mINFO\x1b[0m ',
            '[\x1b[32msqlalchemy\x1b[0m] ',
            '(\x1b[39;49;00m\x1b[34m1L\x1b[39;49;00m,\x1b[39;49;00m)\x1b[39;49;00m\n',
        ]))

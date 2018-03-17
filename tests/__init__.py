import click
from click.testing import CliRunner

from unittest import TestCase

from peerme.main import main, add_internal_modules


class BaseTest(TestCase):

    @classmethod
    def setUpClass(cls):
        add_internal_modules()

    def setUp(self):
        self.runner = CliRunner()
        self.main = main

    def invokeCli(self, *args, **kwargs):
        result = self.runner.invoke(self.main, *args, **kwargs)
        self.assertIsNone(result.exception, result.exception)
        return result


class BasicTests(BaseTest):

    def test_pdbapi(self):
        for command in [
            ('-s', 'pdbapi', 'discover', '-d', '7575'),
            ('-s', 'pdbapi', 'generate', '-d', '9268', '-t', 'ios.template'),
        ]:
            result = self.invokeCli(command)
            self.assertEqual(result.exit_code, 0, result.output)

    # TODO: Come up with a way to test SQL
    # - Hard as we would need to build a MYSQL instance during TravisCI Run
    #    def test_pdbsql(self):
    #        for command in [
    #            ('-s', 'pdbsql', 'discover', '-d', '32934'),
    #            ('-s', 'pdbsql', 'generate', '-d', '15169', '-t', 'generic.template'),
    #        ]:
    #
    #            result = self.invokeCli(command)
    #            self.assertEqual(result.exit_code, 0, result.output)
    def test_euroix(self):
        for command in [
            "-s euroix --refresh-data discover -d 32934",
            "-s euroix discover -d 32934",
            "-s euroix discover -i France-IX",
            "-s euroix discover -d 8218 -i France-IX",
            "-s euroix generate -i France-IX -t ios-xr.template",
            "-s euroix generate -d 8218 -i France-IX -t ios.template",
            "-s euroix generate -d 15169 -t junos.template",
        ]:
            result = self.invokeCli(command.split(' '))
            self.assertEqual(result.exit_code, 0, result.output)

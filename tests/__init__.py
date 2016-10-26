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


class ExampleTests(BaseTest):
    def test_pdbsql(self):
        for command in [
            ('-s', 'pdbsql', 'discover', '-d', '32934'),
            ('-s', 'pdbsql', 'generate', '-d', '15169', '-t', 'generic.template'),
        ]:

            result = self.invokeCli(command)
            self.assertEqual(result.exit_code, 0, result.output)

    def test_pdbapi(self):
        for command in [
            ('-s', 'pdbapi', 'discover', '-d', '32934'),
            ('-s', 'pdbapi', 'generate', '-d', '15169', '-t', 'ios.template'),
        ]:

            result = self.invokeCli(command)
            self.assertEqual(result.exit_code, 0, result.output)

    def test_euroix(self):
        for command in [
            "-s euroix --refresh-data discover -d 32934",
            "-s euroix discover -d 32934",
            "-s euroix discover -i FranceIX-MRS",
            "-s euroix discover -d 8218 -i FranceIX-PAR",
            "-s euroix generate -i FranceIX-PAR -t ios-xr.template",
            "-s euroix generate -d 8218 -i FranceIX-PAR -t ios.template",
            "-s euroix generate -d 15169 -t junos.template",
        ]:
            result = self.invokeCli(command.split(' '))
            self.assertEqual(result.exit_code, 0, result.output)


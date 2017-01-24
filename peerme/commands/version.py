#!/usr/bin/env python3

'''
    Class to Print the current version
'''

import click
import sys

from peerme import __version__


class VersionCli():

    @click.command()
    @click.pass_obj
    def version(cli_opts):
        ''' Displaty PyPI version '''
        click.echo("{} version {}".format(sys.argv[0], __version__))

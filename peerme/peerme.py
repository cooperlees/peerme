#!/usr/bin/env python3

'''
    Discover and Generate IX Peerings
'''

import asyncio
import click
import logging
import sys
import time

from os.path import expanduser

import config as peerme_config
import peerme_db

# TODO: Get relative imports working
# SystemError: Parent module '' not loaded, cannot perform relative import
#from . import (
#    build
#)

CLICK_CONTEXT_SETTINGS = {'help_option_names': ('-h', '--help')}


class PeermeCmd():
    ''' Base class for all sub commands to inherit from '''

    def __init__(self, main_opts):
        ''' Store Global main arguments etc. '''
        self.opts = main_opts





class Options():
    ''' Object for holding shared object between subcommands '''
    def __init__(self, debug, start_time, db, loop, config):
        self.config = config
        self.db = db
        self.debug = debug
        self.loop = loop
        self.start_time = start_time
        self.human_start_time = time.strftime('%Y%m%d%H%M%S',
                                              time.gmtime(start_time))
        logging.debug("{} started @ {}".format(
            sys.argv[0],
            self.human_start_time,
        ))

    def __repr__(self):
        ''' String Representation for debugging '''
        return 'CLI stated @ {} - Debug is {}'.format(
            self.debug,
            self.human_start_time
        )


def _handle_debug(ctx, param, debug):
    '''Turn on debugging if asked otherwise INFO default'''
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format=(
            '[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)'
        ),
        level=log_level
    )
    return debug


@click.group(context_settings=CLICK_CONTEXT_SETTINGS)
@click.option(
    '-c',
    '--config',
    default='{}/.peerme.conf'.format(expanduser('~')),
    help='Config File Location - Default: ~/.peerme.conf',
)
@click.option(
    '-d',
    '--debug',
    is_flag=True,
    help='Turn on verbose logging',
    callback=_handle_debug,
)
@click.pass_context
def main(ctx, config, debug):
    '''
        Discover and generate potential peering endpoints @ IXs

        TODO: Support API calls in ther future as well as a local DB
    '''
    loop = asyncio.get_event_loop()
    config_obj = peerme_config.PeermeConfig()
    # TODO: Move Database config to conf file
    db = peerme_db.PeermeDb(loop)
    loop.run_until_complete(db.get_pool())
    # Class to hold all shared options
    ctx.obj = Options(debug, time.time(), db, loop, config_obj)


def add_internal_modules():
    ''' Add internal modules to main parser '''
    from check_routing import CheckRoutingCli
    main.add_command(CheckRoutingCli().check_routing)
    from discover import DiscoverCli
    main.add_command(DiscoverCli().discover)


if __name__ == '__main__':
    # Add subcommands
    add_internal_modules()
    sys.exit(main())

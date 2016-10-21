#!/usr/bin/env python3

'''
    Discover and Generate IX Peerings
'''

import asyncio
import click
import logging
import sys
import time

import peerme_db
import discover

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
    def __init__(self, debug, start_time, db, loop):
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
    '-d',
    '--debug',
    is_flag=True,
    help='Turn on verbose logging',
    callback=_handle_debug,
)
@click.pass_context
def main(ctx, debug):
    ''' Discover and generate potential peering endpoints @ IXs '''
    loop = asyncio.get_event_loop()
    db = peerme_db.PeermeDb(loop)
    loop.run_until_complete(db.get_pool())
    # Class to hold all shared options
    ctx.obj = Options(debug, time.time(), db, loop)


def add_internal_modules():
    ''' Add internal modules to main parser '''
    main.add_command(discover.DiscoverCli().discover)


if __name__ == '__main__':
    # Add subcommands
    add_internal_modules()
    sys.exit(main())

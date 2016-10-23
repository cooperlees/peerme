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
from peerme import config as peerme_config
from peerme import peerme_db
from peerme import euroix_json
from peerme.commands.check_routing import CheckRoutingCli
from peerme.commands.generate import GenerateConfigCli
from peerme.commands.discover import DiscoverCli
from peerme.commands.request import RequestCli

# TODO: Get relative imports working
# SystemError: Parent module '' not loaded, cannot perform relative import
#from . import (
#    build
#)

CLICK_CONTEXT_SETTINGS = {'help_option_names': ('-h', '--help')}


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
@click.option(
    '-s',
    '--data-source',
    help='Choose datasource to get peers from (pdb, euroix)',
    default='pdb'
)

@click.pass_context
def main(ctx, config, debug, data_source):
    '''
        Discover and generate potential peering endpoints @ IXs

        TODO: Support API calls in ther future as well as a local DB
    '''
    loop = asyncio.get_event_loop()
    config_obj = peerme_config.PeermeConfig(config)
    if data_source == 'pdb':
        peering_api = peerme_db.PeermeDb(loop)
    elif data_source == 'euroix':
        peering_api = euroix_json.PeermeDb(loop)
    else:
        sys.exit("NO VALID OPTIONS FOR ")
    # TODO: Move Database config to conf file
#    loop.run_until_complete(peering_api.get_pool())
    # Class to hold all shared options
    ctx.obj = Options(debug, time.time(), peering_api, loop, config_obj)

def add_internal_modules():
    ''' Add internal modules to main parser '''
    main.add_command(CheckRoutingCli().check_routing)
    main.add_command(DiscoverCli().discover)
    main.add_command(GenerateConfigCli().generate)
    main.add_command(RequestCli().pinder)


if __name__ == '__main__':
    # Add subcommands
    add_internal_modules()
    sys.exit(main())

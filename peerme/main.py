import asyncio
import click
import logging
import sys
import time

from os.path import expanduser
from . import config as peerme_config
from . import peeringdb_mysql
from . import peeringdb_api
from . import euroix_json
from .commands.generate import GenerateConfigCli
from .commands.discover import DiscoverCli
from .commands.request import RequestCli
from .commands.version import VersionCli


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
    '--refresh-data',
    is_flag=True,
    help='Fetch fresh data from Internet sources (EuroIX only)',
)
@click.option(
    '-s',
    '--data-source',
    help='Choose Peering datasource (pdbapi [default], pdbsql, euroix)',
    default='pdbapi'
)
@click.pass_context
def main(ctx, config, debug, data_source, refresh_data):
    '''
        Discover and generate potential peering endpoints @ IXs
    '''

    loop = asyncio.get_event_loop()
    config_obj = peerme_config.PeermeConfig(config)
    if data_source == 'pdbsql':
        peering_api = peeringdb_mysql.PeermeDb(config_obj, loop)
    elif data_source == 'pdbapi':
        peering_api = peeringdb_api.PeermeDb(config_obj, loop)
    elif data_source == 'euroix':
        peering_api = euroix_json.PeermeDb(
            config_obj, refresh_data, loop
        )
    else:
        raise Exception('Invalid option "{}" for data source.'.format(
            data_source))

    # Class to hold all shared options
    ctx.obj = Options(debug, time.time(), peering_api, loop, config_obj)


def add_internal_modules():
    ''' Add internal modules to main parser '''
    main.add_command(DiscoverCli().discover)
    main.add_command(GenerateConfigCli().generate)
    main.add_command(RequestCli().pinder)
    main.add_command(VersionCli().version)


def script_entry():
    # Add subcommands
    add_internal_modules()
    sys.exit(main())


if __name__ == '__main__':
    script_entry()

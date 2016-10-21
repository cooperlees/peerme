#!/usr/bin/env python3

'''
    Class to take care of discovering potential peers
'''

#import asyncio
import click
import logging

# TODO(cooper): Make relative imports work
#from . import peerme
import peerme


class DiscoverCli():

    @click.command()
    @click.option(
        '-y',
        '--yes',
        help='Auto confirm ...',
        is_flag=True,
    )
    @click.pass_obj
    def discover(cli_opts, yes):
        ''' Build a btpkg package and upload to seeders '''
        DiscoverPeers(cli_opts).run(yes)


class DiscoverPeers(peerme.PeermeCmd):
    ''' All Discover related fun '''

    # TODO: Delete
    async def dbTest(self):
        sql_data = await self.opts.db.execute_query()
        print("GOT '{}' from DB".format(sql_data))

    def run(self, yes):
        click.echo("Time to get some peers discovered - Debug = {}".format(
            self.opts.debug
        ))
        click.echo("Yes = {}".format(yes))

        # DB Connection Pool
        self.opts.loop.run_until_complete(self.dbTest())  # DEBUG

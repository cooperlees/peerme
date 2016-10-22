#!/usr/bin/env python3

'''
    Class to discover routing is as desired
'''

import click
import logging

import peerme


class CheckRoutingCli():

    @click.command()
    @click.option(
        '-d',
        '--dest-asn',
        help='Destination ASN for traffic',
    )
    @click.option(
        '-i',
        '--dest-ixp',
        help='Destination IXP for traffic',
    )
    @click.pass_obj
    def discover(cli_opts, dest_asn, dest_ixp):
        ''' Build a btpkg package and upload to seeders '''
        CheckRouting(cli_opts).run(dest_asn, dest_ixp)


class CheckRouting(peerme.PeermeCmd):
    ''' Lets check the traffic paths are as desired '''

    def run(self, dest_asn, dest_ixp):
        pass

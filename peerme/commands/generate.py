#!/usr/bin/env python3

'''
    Class to generate configs from templates in the
    template dir
'''

import click
import logging

from .cli_common import PeermeCmd

from jinja2 import Environment, PackageLoader


class GenerateConfigCli():

    @click.command()
    @click.option(
        '-d',
        '--dest-asn',
        type=int,
        help='Destination ASN for traffic',
    )
    @click.option(
        '-i',
        '--dest-ixp',
        help='Destination IXP for traffic',
    )
    @click.option(
        '-t',
        '--template',
        help='The template to use for config generation',
    )
    @click.pass_obj
    def generate(cli_opts, dest_asn, dest_ixp, template):
        ''' Generate rendered templates using the found peerings '''
        GenerateConfig(cli_opts).run(dest_asn, dest_ixp, template)


class GenerateConfig(PeermeCmd):

    def _template_render(self, template, peer):
        ''' Get Data and render the template '''
        env = Environment(loader=PackageLoader('peerme', '../templates'))
        template = env.get_template(template)
        return template.render(peer=peer)

    def run(self, dest_asn, dest_ixp, template):
        self.opts.db.MY_ASN = self.opts.config.config['peerme']['my_asn']
        if dest_asn:
            peers_result = self.opts.loop.run_until_complete(
                self.opts.db.get_session_by_asn(dest_asn)
            )
            for peer in peers_result:
                click.echo(self._template_render(template, peer))

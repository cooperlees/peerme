#!/usr/bin/env ptyhon3

import aiohttp
import asyncio
import ipaddress
import logging
import json
import sys

from . import peer


class RestAPIException(Exception):
    ''' Exception to handle HTTP errors '''
    def __init__(self, endpoint, query, http_code):
        self.endpoint = endpoint
        self.query = query
        self.full_query = '{}/{}'.format(endpoint, query)
        self.http_code = http_code

    def __repr__(self):
        return '{} returned {}'.format(self.full_query, self.http_code)


class PeeringDB():
    def __init__(self, config, loop=None):
        self.loop = loop if loop else asyncio.get_event_loop()
        self.global_config = config.config

    def validate_ip_address(self, address, af=6):
        if af == 4:
            try:
                ipaddress.IPv4Address(address)
                return True
            except ipaddress.AddressValueError as ex:
                logging.error(ex)
        elif af == 6:
            try:
                ipaddress.IPv6Address(address)
                return True
            except ipaddress.AddressValueError as ex:
                logging.error(ex)
        else:
            raise Exception("Invalid AF: {}".format(af))
        return False

    async def get_session_by_asn(self, asn):
        '''
        Find all sessions we can peer with this ASN.
        TODO:
        - Validation:
        -- Validate that the IPs configured are in the same subnet as the fabric
        - data:
        -- get prefix limits
        -- get as-set data
        There are some edge cases we miss here (possibly more):
        - We only look for the ASN if there are multiple ASNs we only find
            the one provided
        '''
        peers = []

        try:
            peer_name = await self.get_peername_by_asn(asn)
        except RestAPIException as apie:
            # If the ASN does not exist no point running
            sys.exit(2)

        my_asn = self.global_config['peerme']['my_asn']
        peerdb_tasks = [
            self.get_fid_asn(asn),
            self.get_prefixlimits_by_asn(asn),
            self.get_fid_asn(my_asn),
        ]
        tasks_output = await asyncio.gather(*peerdb_tasks)
        peer_fids = tasks_output[0]
        prefix_limit_v4, prefix_limit_v6 = tasks_output[1]
        my_fids = tasks_output[2]

        common_fids = list(set(my_fids) & set(peer_fids))
        for fid in common_fids:

            fid_tasks = [
                self.get_ips_by_asn_fid(asn, fid),
                self.get_fidname_by_fid(fid),
            ]
            tasks_output = await asyncio.gather(*fid_tasks)
            ips_in_fid = tasks_output[0]
            fidname = tasks_output[1]

            for ip in ips_in_fid:
                this_peer = peer.Peer()
                this_peer.asn = asn
                this_peer.name = peer_name
                this_peer.ix_desc = fidname
                if self.validate_ip_address(ip.get('ipaddr4'), 4):
                    this_peer.peer_ipv4 = ip.get('ipaddr4')
                if self.validate_ip_address(ip.get('ipaddr6'), 6):
                    this_peer.peer_ipv6 = ip.get('ipaddr6')
                this_peer.prefix_limit_v4 = prefix_limit_v4
                this_peer.prefix_limit_v6 = prefix_limit_v6
                peers.append(this_peer)
        return peers

    async def get_session_by_ix(self, ix_name):

        raise NotImplementedError('get_session_by_ix not supported')

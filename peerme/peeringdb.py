#!/usr/bin/env ptyhon3

import aiohttp
import asyncio
import ipaddress
import logging
import json
import sys

from . import peer

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
        peerdb_tasks = []
        peers = []

        # Potential AsyncIO Tasks
        peer_fids = await self.get_fid_asn(asn)
        peer_name = await self.get_peername_by_asn(asn)
        prefix_limit_v4, prefix_limit_v6 = await self.get_prefixlimits_by_asn(asn)
        my_fids = await self.get_fid_asn(
            self.global_config['peerme']['my_asn'])

        common_fids = list(set(my_fids) & set(peer_fids))
        for fid in common_fids:

            # Batch these two for each loop iteration
            ips_in_fid = await self.get_ips_by_asn_fid(asn, fid)
            fidname = await self.get_fidname_by_fid(fid)

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

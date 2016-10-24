#!/usr/bin/env python3

import aiohttp
import asyncio
import json
import logging
import sys

from . import peeringdb


class PeermeDb(peeringdb.PeeringDB):
    PEERINGDB_API = 'https://peeringdb.com/api/'

    def __init__(self, config, loop=None, api_url=None):
        super().__init__(config, loop)
        # Allow custom URL in a instance if required
        if api_url:
            self.PEERINGFB_API = api_url

        # Host the ASN Result in Memory
        self.ASN_NET_RESULT = None

    async def execute_query(self, endpoint, query):
        '''
            Connect using aiohttp to Rest endpoints

            If we don't get a valid response fire a RestAPIException
        '''
        url = '{}{}'.format(self.PEERINGDB_API, endpoint)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=query) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get('data')
                else:
                    raise peeringdb.RestAPIException(url, query, resp.status)

    async def get_fid_asn(self, asn):
        '''
        Get all the fabrics that an ASN participates on.
        '''
        fids = []
        result = await self.execute_query(
            'netixlan',
            {'asn': asn})

        fids = [f['ix_id'] for f in result]
        return fids

    async def get_ips_by_asn_fid(self, asn, fid):
        '''
        Get all the IPs that an ASN has on a fabric.
        '''
        result = await self.execute_query(
            'netixlan',
            {'asn': asn, 'ix_id': fid})
        return result

    async def get_fidname_by_fid(self, fid):
        '''
        Get the long name of the fabric to use as a identifier.
        '''
        result = await self.execute_query(
            'ix',
            {'id': fid})
        if result:
            result = result[0].get('name')
        return result

    async def get_peername_by_asn(self, asn):
        '''
        Grab the peer name from peeringdb
        '''
        peer_name = None
        if not self.ASN_NET_RESULT:
            try:
                result = await self.execute_query(
                    'net',
                    {'asn': asn}
                )
                peer_name = result[0]['name']
                self.ASN_NET_RESULT = result
            except peeringdb.RestAPIException as apie:
                err = ('Unable to find ASN {}\'s name. Exiting. '
                       '({} returned {})'.format(
                       asn, apie.full_query, apie.http_code))
                logging.error(err)
                raise
        else:
            peer_name = self.ASN_NET_RESULT[0]['name']
            logging.debug('Using cached ASN_NET_RESULT in get_peername_by_asn')  # COOPER

        return peer_name

    async def get_prefixlimits_by_asn(self, asn):
        '''
        Grab the prefix limits from peeringdb
        '''
        prefix_limit_v4 = None
        prefix_limit_v6 = None

        if not self.ASN_NET_RESULT:
            result = await self.execute_query(
                'net',
                {'asn': asn})
        else:
            result = self.ASN_NET_RESULT
            logging.debug('Using cached ASN_NET_RESULT in get_prefixlimits_by_asn')  # COOPER

        if result:
            result = result[0]
            prefix_limit_v4 = int(result.get('info_prefixes4'))
            prefix_limit_v6 = int(result.get('info_prefixes6'))

        return prefix_limit_v4, prefix_limit_v6

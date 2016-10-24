#!/usr/bin/env python3

import aiohttp
import asyncio
import json
import logging
import sys

from . import peeringdb

class PeermeDb(peeringdb.PeeringDB):
    PEERINGDB_API = 'https://peeringdb.com/api/'

    async def execute_query(self, endpoint, query):
        url = '{}{}'.format(self.PEERINGDB_API, endpoint)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=query) as resp:
                assert resp.status == 200
                result = await resp.json()
                return result.get('data')

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
        TODO: Validate that we actually get data back here.
        '''
        fids = []
        result = await self.execute_query(
            'net',
            {'asn': asn})
        peer_name = result[0]['name']
        return peer_name

    async def get_prefixlimits_by_asn(self, asn):
        '''
        Grab the prefix limits from peeringdb
        '''
        result = await self.execute_query(
            'net',
            {'asn': asn})
        if result:
            result = result[0]
            prefix_limit_v4 = int(result.get('info_prefixes4'))
            prefix_limit_v6 = int(result.get('info_prefixes6'))
        return prefix_limit_v4, prefix_limit_v6

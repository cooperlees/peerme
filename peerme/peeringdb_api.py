import asyncio
import logging
import aiohttp
import json

import concurrent.futures
import sys

from . import peer

class PeermeDb():
    PEERINGDB_API = 'https://peeringdb.com/api/'

    def __init__(self, loop=None):
        self.loop = loop if loop else asyncio.get_event_loop()

    async def execute_query(query):
        url = '{}{}'.format(self.PEERINGDB_API, query)
        response = await aiohttp.request('GET', url)
        await response.close()
        if response.status != 200:
            raise Exception('Too few 200s:\n{}'.format(response))
        return json.loads(response.json())

    async def get_fid_asn(self, asn):
        '''
        Get all the fabrics that an ASN participates on.
        '''
        base_query = (
            'SELECT ix_id '
            'FROM peeringdb_network_ixlan '
            'JOIN peeringdb_ixlan ON ixlan_id = peeringdb_ixlan.id '
            'WHERE asn={asn} GROUP BY ix_id;')
        base_query = (
            'netixlan?asn={ASN}')
        )
        query = base_query.format(ASN=asn)

        result = await self.execute_query(query)
        for ixlan_result in result:
            print(ixlan_result)

        return result


    async def get_ips_by_asn_fid(self, asn, fid):
        '''
        Get all the IPs that an ASN has on a fabric.
        '''
        base_query = (
            'SELECT ipaddr4, ipaddr6 FROM peeringdb_network_ixlan '
            'JOIN peeringdb_ixlan ON ixlan_id = peeringdb_ixlan.id '
            'WHERE ix_id={FID} AND asn = {ASN}')
        query = base_query.format(FID=fid, ASN=asn)
        result = await self.execute_query(query)
        return result

    async def get_fidlongname_by_fid(self, fid):
        '''
        Get the long name of the fabric to use as a identifier.
        '''
        base_query = (
            'SELECT name_long FROM peeringdb_ix '
            'WHERE id=\'{FID}\'')
        query = base_query.format(FID=fid)
        result = await self.execute_query(query)
        if result:
            result = result[0].get('name_long')
        return result

    async def get_fidname_by_fid(self, fid):
        '''
        Get the long name of the fabric to use as a identifier.
        '''
        base_query = (
            'SELECT name FROM peeringdb_ix '
            'WHERE id=\'{FID}\'')
        query = base_query.format(FID=fid)
        result = await self.execute_query(query)
        if result:
            result = result[0].get('name')
        return result

    async def get_peername_by_asn(self, asn):
        '''
        Grab the peer name from peeringdb
        '''
        base_query = (
            'SELECT name FROM peeringdb_network WHERE asn={ASN}')
        query = base_query.format(ASN=asn)
        result = await self.execute_query(query)
        if result:
            result = result[0].get('name')
        return result

    async def get_prefixlimits_by_asn(self, asn):
        '''
        Grab the prefix limits from peeringdb
        '''
        base_query = (
            'SELECT info_prefixes4, info_prefixes6 '
            'FROM peeringdb_network WHERE asn={ASN}')
        query = base_query.format(ASN=asn)
        result = await self.execute_query(query)
        if result:
            result = result[0]
            prefix_limit_v4 = result.get('info_prefixes4')
            prefix_limit_v6 = result.get('info_prefixes6')
        return prefix_limit_v4, prefix_limit_v6

    async def get_session_by_asn(self, asn):
        '''
        Find all sessions we can peer with this ASN.
        '''
        peers = []
        peer_fids = await self.get_fid_asn(asn)
        sys.exit(1)
        peer_fids = [f['ix_id'] for f in peer_fids]
        my_fids = await self.get_fid_asn(self.MY_ASN)
        my_fids = [f['ix_id'] for f in my_fids]
        common_fids = list(set(my_fids) & set(peer_fids))
        peer_name = await self.get_peername_by_asn(asn)
        prefix_limit_v4, prefix_limit_v6 = await self.get_prefixlimits_by_asn(asn)
        for fid in common_fids:
            ips_in_fid = await self.get_ips_by_asn_fid(asn, fid)
            fidlongname = await self.get_fidlongname_by_fid(fid)
            for ip in ips_in_fid:
                this_peer = peer.Peer()
                this_peer.asn = asn
                this_peer.name = peer_name
                this_peer.ix_desc = fidlongname
                this_peer.peer_ipv4 = ip.get('ipaddr4')
                this_peer.peer_ipv6 = ip.get('ipaddr6')
                this_peer.prefix_limit_v4 = prefix_limit_v4
                this_peer.prefix_limit_v6 = prefix_limit_v6
                peers.append(this_peer)
        return peers

    async def get_session_by_ix(self, ipv4_subnet):
        raise NotImplementedError('get_session_by_ix not supported')

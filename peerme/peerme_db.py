#!/usr/bin/env python3

'''
    Handle all aiomysql interactions
'''

import asyncio
import logging

import sys

import peer
import aiomysql
from pymysql import err as pymysql_err

class PeermeDb():

    # TODO: Move to Config File
    HOST = 'localhost'
    USER = 'peeringdb'
    PASS = 'l33tasbr0'
    PORT = 3306
    DATABASE = 'peeringdb'
    MY_ASN = 32934

    def __init__(self, loop=None):
        self.loop = loop if loop else asyncio.get_event_loop()

    # TODO: Maybe move to an async with usage possibly
#    def __aenter__(self):
#        pass
#
#    def __aexit__(self):
#        pass

    async def get_pool(self):
        try:
            self.pool = await aiomysql.create_pool(
                host=self.HOST,
                port=self.PORT,
                user=self.USER,
                password=self.PASS,
                db=self.DATABASE,
                loop=self.loop,
            )
        except pymysql_err.OperationalError as pmye:
            logging.critical("DB Connect Error: {}".format(pmye))
            sys.exit(1)

    # TODO: Remove sample function
    async def execute_query(self, query='SELECT 42;'):
        await self.get_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query)
                #print(cur.description)  # Cooper
                rows = await cur.fetchall()
        self.pool.close()
        await self.pool.wait_closed()
        return rows

    async def get_fid_asn(self, asn):
        '''
        Get all the fabrics that an ASN participates on.
        '''
        base_query = (
            'SELECT ix_id '
            'FROM peeringdb_network_ixlan '
            'JOIN peeringdb_ixlan ON ixlan_id = peeringdb_ixlan.id '
            'WHERE asn={asn} GROUP BY ix_id;')
        query = base_query.format(asn=asn)
        result = await self.execute_query(query)
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

    async def get_session_by_asn(self, asn):
        '''
        Find all sessions we can peer with this ASN.
        TODO:
        - Validation:
        -- Validate that the IPs configured are in the same subnet as the fabric
        - data:
        -- get prefix limits
        -- get as-set data
        - performance:
        -- these queries can be improved a lot, or we do better queries
        There are some edge cases we miss here (possibly more):
        - We only look for the ASN if there are multiple ASNs we only find
            the one provided
        '''
        peers = []
        peer_fids = await self.get_fid_asn(asn)
        peer_fids = [f['ix_id'] for f in peer_fids]
        my_fids = await self.get_fid_asn(self.MY_ASN)
        my_fids = [f['ix_id'] for f in my_fids]
        common_fids = list(set(my_fids) & set(peer_fids))
        for fid in common_fids:
            ips_in_fid = await self.get_ips_by_asn_fid(asn, fid)
            print(ips_in_fid)
            fidlongname = await self.get_fidlongname_by_fid(fid)
            for ip in ips_in_fid:
                this_peer = peer.Peer()
                this_peer.asn = asn
                this_peer.ix_desc = fidlongname
                this_peer.peer_ipv4 = ip.get('ipaddr4')
                this_peer.peer_ipv6 = ip.get('ipaddr6')
                peers.append(this_peer)
        return peers

    def get_session_by_ix(self, ipv4_subnet):
        raise NotImplementedError('get_session_by_ix not supported')

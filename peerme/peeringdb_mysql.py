#!/usr/bin/env python3

'''
    Handle all aiomysql interactions
'''

import asyncio
import logging

import sys

import aiomysql
from pymysql import err as pymysql_err
from . import peeringdb

class PeermeDb(peeringdb.PeeringDB):
    async def get_pool(self):
        HOST = self.global_config['peeringdb_mysql']['host']
        USER = self.global_config['peeringdb_mysql']['user']
        PASS = self.global_config['peeringdb_mysql']['pass']
        PORT = int(self.global_config['peeringdb_mysql']['port'])
        DATABASE = self.global_config['peeringdb_mysql']['database']
        try:
            self.pool = await aiomysql.create_pool(
                host=HOST,
                port=PORT,
                user=USER,
                password=PASS,
                db=DATABASE,
                loop=self.loop,
            )
        except pymysql_err.OperationalError as pmye:
            logging.critical("DB Connect Error: {}".format(pmye))
            sys.exit(1)

        logging.debug("Obtained DB connection pool to {}".format(HOST))

    async def execute_query(self, query):
        if not self.pool:
            await self.get_pool()

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query)
                rows = await cur.fetchall()

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
        return [f['ix_id'] for f in result]

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

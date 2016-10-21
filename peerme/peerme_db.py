#!/usr/bin/env python3

'''
    Handle all aiomysql interactions
'''

import asyncio
import logging
import sys

import aiomysql
from pymysql import err as pymysql_err


class PeermeDb():

    # TODO: Move to Config File
    HOST = 'localhost'
    USER = 'peeringdb'
    PASS = 'l33tasbr0'
    PORT = 3306
    DATABASE = 'peeringdb'

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
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                print(cur.description)  # Cooper
                rows = await cur.fetchall()

        return rows

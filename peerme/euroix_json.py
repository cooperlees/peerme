#!/usr/bin/env python3

'''
    Where we make the things for EuroIX JSON
'''

import aiohttp
import asyncio
import async_timeout
import glob
import json
import logging
import re
import time

from . import peer

class PeermeDb():
    '''
        Replaces talking to the Peering DB and generates output based on
        EuroIX JSON data

        We HTTP download the data and cache locally
    '''

    #this gets JSON files from IXP and save it with proper names
    BASE_PATH = 'peerme/euroix-json/'

    def __init__(self, config, refresh_data=False, loop=None):
        self.global_config = config.config
        self.HTTP_TIMEOUT = int(self.global_config['peerme']['http_timeout'])
        self.loop = loop if loop else asyncio.get_event_loop()
        if refresh_data:
            self.fetch_json('peerme/euroix-list.json')

    async def _get_via_http(self, url):
        ''' async JSON fetching coro '''
        try:
            async with aiohttp.ClientSession(loop=self.loop) as session:
                with async_timeout.timeout(self.HTTP_TIMEOUT):
                    async with session.get(url) as response:
                        data = await response.text()
        except Exception as e:
            logging.error("{} unable to be fetched: {}".format(
                url, str(e)), exc_info=True,
            )
            data = None

        return url, data

    def fetch_json(self, ixp_json_file):
        async_json_fetch_start = time.time()
        with open(ixp_json_file, 'r') as f:
            ixp_data_urls = json.load(f)
        logging.info("Refreshing {} IXP JSON Datasets".format(
            len(ixp_data_urls)
        ))

        http_tasks = [
            asyncio.ensure_future(
                self._get_via_http(url)
            ) for url in ixp_data_urls
        ]
        completed_tasks, _ = self.loop.run_until_complete(
            asyncio.wait(http_tasks, timeout=self.HTTP_TIMEOUT)
        )

        for task in completed_tasks:
            url, data = task.result()
            if not data:
                continue
            logging.debug("Writing {} to disk".format(url))
            ixp = json.loads(data)
            # Strip everyting after the first space
            file_name = re.sub(' .*$', '', ixp['ixp_list'][0]['shortname'])

            # Make London Great Again - Hack
            if file_name == "London":
                file_name = "LINX"

            # TODO: Lets do smarter caching and in memory storage + be atomic
            with open(self.BASE_PATH + file_name, 'w') as out_file:
                out_file.write(data)

        fetch_time = time.time() - async_json_fetch_start
        logging.debug("HTTP JSON data fetch took {} seconds".format(fetch_time))

    def session_on_all_ixp(self):
        ''' Gives all the sessions on all the IXP we have '''
        full_peers_list = []
        file_list = glob.glob(self.BASE_PATH + "*")
        for filename in file_list:
            #stripping foler name
            filename = re.sub('^.*\/', '', filename)
            #get the list per IXP and merge it
            peers_list = self.session_by_ix(filename)
            for peer in peers_list:
                full_peers_list.append(peer)
        return full_peers_list

    # gives the list of sessions you could establish on an IXP
    # if my_asn is provided, it will remove it from the list
    async def get_session_by_ix(self, ix_name, my_asn=None):
        my_asn = self.global_config['peerme']['my_asn']
        peers_list = []
        #open the file for the givent IXP
        with open(self.BASE_PATH + ix_name, 'r') as f:
            data = json.load(f)
            #there can be several IXP in one file (AMS-IX HK, Chicago, etc...)
            for ixp in data['ixp_list']:
                try:
                    # name is not mandarory, shortname is
                    ixp_name = ixp["name"]
                except KeyError:
                    ixp_name = ixp["shortname"]
                for member in data['member_list']:
                    if not member:
                        logging.debug('Empty member on: {}'.format(ixp_name))
                        continue
                    if 'connection_list' not in member:
                        logging.debug(
                            'Member doens\'t have any connections:'
                            ' {} {}'.format(ixp_name, member))
                        continue
                    #a member can have several connections on the same IXP/LAN
                    for connection in member["connection_list"]:
                        my_peer = peer.Peer()
                        #my_peer.ix_desc = ixp_name
                        my_peer.ix_desc = ixp["shortname"]
                        #connection_list list connections for all IXP in the file...
                        if ixp["ixp_id"] == connection["ixp_id"]:
                            my_peer.asn = member["asnum"]
                            my_peer.name = member["name"]
                            try:
                                for vlan in connection["vlan_list"]:
                                    my_peer.peer_ipv4 = vlan["ipv4"]["address"]
                                    try:
                                        my_peer.peer_ipv6 = vlan["ipv6"]["address"]
                                    except KeyError:
                                        #because LINX has problem with IPv6
                                        my_peer.peer_ipv6 = ''
                                    for inetF in ["ipv4", "ipv6"]:
                                        for optionals in ["max_prefix", "as_macro"]:
                                            try:
                                                vlan[inetF][optionals]
                                            except KeyError:
                                                 pass
                                            else:
                                                if inetF == "ipv4" and optionals == "max_prefix": my_peer.prefix_limit_v4 = vlan[inetF][optionals]
                                                if inetF == "ipv6" and optionals == "max_prefix": my_peer.prefix_limit_v6 = vlan[inetF][optionals]
                                                if inetF == "ipv4" and optionals == "as_macro": my_peer.as_set_v4 = vlan[inetF][optionals]
                                                if inetF == "ipv6" and optionals == "as_macro": my_peer.as_set_v6 = vlan[inetF][optionals]
                            except KeyError:
                                 pass
                            except TypeError:
                                try:
                                    #this case is due to AMS-IX not properly using vlan_list yet
                                    my_peer.peer_ipv4 = connection["vlan_list"]["ipv4"]["address"]
                                    my_peer.peer_ipv6 = connection["vlan_list"]["ipv6"]["address"]
                                    for inetF in ["ipv4", "ipv6"]:
                                        for optionals in ["max_prefix", "as_macro"]:
                                            try:
                                                connection["vlan_list"][inetF][optionals]
                                            except KeyError:
                                                 pass
                                            else:
                                                if inetF == "ipv4" and optionals == "max_prefix": my_peer.prefix_limit_v4 = connection["vlan_list"][inetF][optionals]
                                                if inetF == "ipv6" and optionals == "max_prefix": my_peer.prefix_limit_v6 = connection["vlan_list"][inetF][optionals]
                                                if inetF == "ipv4" and optionals == "as_macro": my_peer.as_set_v4 = connection["vlan_list"][inetF][optionals]
                                                if inetF == "ipv6" and optionals == "as_macro": my_peer.as_set_v6 = connection["vlan_list"][inetF][optionals]
                                except KeyError:
                                    pass
                            #special case if my_asn is declared (don't add it to the list)
                            if (my_asn is None) or (my_asn != my_peer.asn ):
                                peers_list.append( my_peer )
        return peers_list

    # gives the list of sessions you could establish with asn
    # if my_asn is provided, it will only return the list of sessions on IXP you have in common
    async def get_session_by_asn(self, asn):
        my_asn = self.global_config['peerme']['my_asn']
        peers_list = []
        file_list = glob.glob(self.BASE_PATH + "*")
        #load all files in order to seek on all IXP
        for filename in file_list:
            #stripping foler name
            filename = re.sub('^.*\/', '', filename)
            ixp_peers_list = await self.get_session_by_ix(filename)
            #we seek on the peers_list if my_asn is present and mark it
            present = []
            for peer in ixp_peers_list:
                if peer.asn == int(my_asn):
                    present.append(peer.ix_desc)
            #we seek for the asn we want to peer with, and make sure we are on the same IX
            for peer in ixp_peers_list:
                if peer.asn == int(asn) and peer.ix_desc in present:
                    #add peer to peers_list if my_asn in not define OR my_asn is present
                    if (my_asn and present) or my_asn is None:
                        peers_list.append(peer)
        return peers_list

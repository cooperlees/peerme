#!/usr/bin/env python3

'''
    Where we make the things for EuroIX JSON
'''

import json
import urllib.request
from pprint import pprint
import re
import glob
import asyncio

from . import peer

class PeermeDb():
    BASE_PATH = 'peerme/euroix-json/'
    #this gets JSON files from IXP and save it with proper names
    def __init__(self, loop=None):
        self.loop = loop if loop else asyncio.get_event_loop()

    def fetch_json(self, file):
        with open(file, 'r') as f:
            data = json.load(f)

        for url in data:
            print("url = "+url)
            #urllib.request.urlretrieve(url, "euroix-json/file_name")
            response = urllib.request.urlopen(url)
            data = response.read()
            ixp = json.loads(data.decode('utf-8'))
            #strip everyting after the first space
            file_name = re.sub(' .*$', '', ixp['ixp_list'][0]['shortname'])
            #little evil hach....
            if file_name == "London":
                file_name = "LINX"
            with open(self.BASE_PATH + file_name, 'wb') as out_file:
                out_file.write(data)
        return


    #gives all the sessions on all the IXP we have
    def session_on_all_ixp(self):
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
    def get_session_by_ix(self, IX_name, my_asn=None):
        peers_list = [ ]
        #open the file for the givent IXP
        with open(self.BASE_PATH + IX_name, 'r') as f:
            data = json.load(f)
            #there can be several IXP in one file (AMS-IX HK, Chicago, etc...)
            for ixp in data['ixp_list']:
                try:
                    # name is not mandarory, shortname is
                    ixp["name"]
                except KeyError:
                    ixp_name = ixp["shortname"]
                else:
                    ixp_name = ixp["name"]

                for member in data['member_list']:
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
                                    my_peer.peer_ipv6 = vlan["ipv6"]["address"]
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
        my_asn = self.MY_ASN
        print(my_asn)
        peers_list = []
        file_list = glob.glob(self.BASE_PATH + "*")
        #load all files in order to seek on all IXP
        for filename in file_list:
            #stripping foler name
            filename = re.sub('^.*\/', '', filename)
            ixp_peers_list = self.get_session_by_ix(filename)
            #we seek on the peers_list if my_asn is present
            present = False
            for peer in ixp_peers_list:
                if peer.asn == int(my_asn):
                    present = True
            for peer in ixp_peers_list:
                if peer.asn == int(asn):
                    #add peer to peers_list if my_asn in not define OR my_asn is present
                    if (my_asn and present) or my_asn is None:
                        peers_list.append(peer)
        return peers_list


    #############

    ##this is use to fill the forder with JSON
    #fetch_json('euroix-list.json')
    #peers_list = session_on_all_ixp()
    #peers_list = session_by_ix("FranceIX-MRS") #the list of peers for FranceIX-MRS
    #peers_list = session_by_ix("FranceIX-MRS", 8218) #the list of peers for FranceIX-MRS without 8218
    #peers_list = session_by_asn(15169) #the list of all sessions of Google
    #peers_list = session_by_asn(15169, 32934) #the list of all sessions of Google where Facebook is present on the IXP
    #for peer in peers_list: print(peer.ix_desc, peer.name, peer.asn, peer.peer_ipv4, peer.peer_ipv6, peer.prefix_limit_v4, peer.prefix_limit_v6, peer.as_set_v4, peer.as_set_v6)

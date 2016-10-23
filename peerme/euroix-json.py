#!/usr/bin/env python3

'''
	Where we make the things for EuroIX JSON
'''

import json
import urllib.request
from pprint import pprint
import re
import glob

from peer import Peer

debug = False


#this gets JSON files from IXP and save it with proper names
def fetch_json( file ):
	
	with open(file, 'r') as f:
		data = json.load(f)
		
	for url in data:
		print("url = "+url)
		#urllib.request.urlretrieve(url, "euroix-json/file_name")
		response = urllib.request.urlopen(url)
		data = response.read()
		ixp = json.loads(data.decode('utf-8'))
		if debug: print("shortname = " + ixp['ixp_list'][0]['shortname'])
		#strip everyting after the first space
		file_name = re.sub(' .*$', '', ixp['ixp_list'][0]['shortname'])
		#little evil hach....
		if file_name == "London":
			file_name = "LINX"
		with open('euroix-json/' + file_name, 'wb') as out_file:
			out_file.write(data)
	return



def list_files():
	file_list = glob.glob("euroix-json/*")
	for filename in file_list:
		if debug: print(filename)
		#stripping foler name
		filename = re.sub('^.*\/', '', filename)
		if debug: print(filename)
		peers_list = session_by_ix(filename)
		for peer in peers_list: print(peer.ix_desc,peer.asn,peer.peer_ipv4,peer.peer_ipv6, peer.prefix_limit_v4, peer.prefix_limit_v6, peer.as_set_v4, peer.as_set_v6)


def session_by_ix( IX_name ):
	peers_list = [ ]
	with open('euroix-json/'+IX_name, 'r') as f:
		data = json.load(f)
		#pprint(data)
		for ixp in data['ixp_list']:
			try:
				ixp["name"]
			except KeyError:
				ixp_name = ixp["shortname"]
			else:
				ixp_name = ixp["name"]
			print(ixp_name + " : " + str(ixp["ixp_id"]))
			
			for member in data['member_list']:
				for connection in member["connection_list"]:
					my_peer = Peer()
					my_peer.ix_desc = ixp["shortname"]
					if ixp["ixp_id"] == connection["ixp_id"]:
						if debug: print(member["asnum"])
						my_peer.asn = member["asnum"]
						try: 
							for vlan in connection["vlan_list"]:
								my_peer.peer_ipv4 = vlan["ipv4"]["address"]
								my_peer.peer_ipv6 = vlan["ipv6"]["address"]
								for inetF in ["ipv4", "ipv6"]:
									if debug: print(vlan[inetF]["address"])
									for optionals in ["max_prefix", "as_macro"]:
										try: 
											vlan[inetF][optionals]
										except KeyError:
											 pass
										else: 
											if debug: print(vlan[inetF][optionals])
											if inetF == "ipv4" and optionals == "max_prefix": my_peer.prefix_limit_v4 = vlan[inetF][optionals]
											if inetF == "ipv6" and optionals == "max_prefix": my_peer.prefix_limit_v6 = vlan[inetF][optionals]
											if inetF == "ipv4" and optionals == "as_macro": my_peer.as_set_v4 = vlan[inetF][optionals]
											if inetF == "ipv6" and optionals == "as_macro": my_peer.as_set_v6 = vlan[inetF][optionals]
						except KeyError:
							 pass
						except TypeError:
							#if debug: print("AMS-IX Crappy!")
							try: 
								my_peer.peer_ipv4 = connection["vlan_list"]["ipv4"]["address"]
								my_peer.peer_ipv6 = connection["vlan_list"]["ipv6"]["address"]
								for inetF in ["ipv4", "ipv6"]:
									if debug: print(connection["vlan_list"][inetF]["address"])
									for optionals in ["max_prefix", "as_macro"]:
										try: 
											connection["vlan_list"][inetF][optionals]
										except KeyError:
											 pass
										else: 
											if debug: print(vlan[inetF][optionals])
											if inetF == "ipv4" and optionals == "max_prefix": my_peer.prefix_limit_v4 = connection["vlan_list"][inetF][optionals]
											if inetF == "ipv6" and optionals == "max_prefix": my_peer.prefix_limit_v6 = connection["vlan_list"][inetF][optionals]
											if inetF == "ipv4" and optionals == "as_macro": my_peer.as_set_v4 = connection["vlan_list"][inetF][optionals]
											if inetF == "ipv6" and optionals == "as_macro": my_peer.as_set_v6 = connection["vlan_list"][inetF][optionals]
							except KeyError:
								pass
						peers_list.append( my_peer )
						#peer = my_peer
						#print(peer.ix_desc,peer.asn,peer.peer_ipv4,peer.peer_ipv6)
	return peers_list


#this is use to fill the forder with JSON
#fetch_json('euroix-list.json')
list_files()
#peers_list = session_by_ix("FranceIX-MRS")
#for peer in peers_list: print(peer.ix_desc,peer.asn,peer.peer_ipv4,peer.peer_ipv6, peer.prefix_limit_v4, peer.prefix_limit_v6, peer.as_set_v4, peer.as_set_v6)

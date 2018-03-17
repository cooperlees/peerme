#!/usr/bin/env python3
import ipaddress


class Peer():

    def __init__(self):
        self.asn = int()
        self.ix_desc = str()
        self.peer_ipv4 = ipaddress.IPv4Address
        self.peer_ipv6 = ipaddress.IPv6Address
        self.prefix_limit_v4 = int(101)
        self.prefix_limit_v6 = int(101)
        self.as_set_v4 = str()
        self.as_set_v6 = str()
        self.name = str()

    def __repr__(self):
        base_string = (
            '<{NAME}: IX: {IX}, ASN: {ASN}, '
            'IPv4: {PEER_IPV4}, IPv4 Limit: {IPV4_LIMIT}, '
            'IPv6: {PEER_IPV6}, IPv6 Limit: {IPV6_LIMIT}>'
        )
        peer_string = base_string.format(
            NAME=self.name,
            IX=self.ix_desc,
            ASN=self.asn,
            PEER_IPV4=self.peer_ipv4,
            IPV4_LIMIT=self.prefix_limit_v4,
            IPV6_LIMIT=self.prefix_limit_v6,
            PEER_IPV6=self.peer_ipv6,
        )
        return peer_string

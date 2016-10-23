#!/usr/bin/env python3
class Peer():
    def __init__(self):
        self.asn = ''
        self.ix_desc = ''
        self.peer_ipv4 = None
        self.peer_ipv6 = None
        self.prefix_limit_v4 = None
        self.prefix_limit_v6 = None
        self.as_set_v4 = None
        self.as_set_v6 = None
        self.name = None

    def __repr__(self):
        base_string = (
            '<IX: {IX}, ASN: {ASN}, '
            'IPv4: {PEER_IPV4}, IPv4 Limit: {IPV4_LIMIT}, '
            'IPv6: {PEER_IPV6}, IPv6 Limit: {IPV6_LIMIT}>')
        peer_string = base_string.format(
            IX=self.ix_desc,
            ASN=self.asn,
            PEER_IPV4=self.peer_ipv4,
            IPV4_LIMIT=self.prefix_limit_v4,
            IPV6_LIMIT=self.prefix_limit_v6,
            PEER_IPV6=self.peer_ipv6,
        )
        return peer_string

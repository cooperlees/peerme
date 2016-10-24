# peerme
Tool to discover and generate possible peerings between Internet Autonomous Systems

GOAL: Make Peering Great Again!

```
"peerme discover" gives a list of IP and IXP you have in common with a specified ASN.
<<<<<<< HEAD
"peerme genetate" make the configuration from a template.
```
=======
"peerme generate" make the configuration from a template.
>>>>>>> cooperlees/master

# Requirements
* Python >= 3.5
* pip modules:
    * aiomysql: https://github.com/aio-libs/aiomysql
  * (if not using PeeringDB API)
  * aiohttp: http://aiohttp.readthedocs.io/
  * click: http://click.pocoo.org/
  * jinja2: http://jinja.pocoo.org/

# Usage
```
Usage: peerme.py [OPTIONS] COMMAND [ARGS]...

  Discover and generate potential peering endpoints @ IXs

Options:
  -c, --config TEXT       Config File Location - Default: ~/.peerme.conf
  -d, --debug             Turn on verbose logging
  --refresh-data          Fetch fresh data from Internet sources (EuroIX only)
  -s, --data-source TEXT  Choose datasource to get peers from (pdbsql, pdbapi, euroix)
  -h, --help              Show this message and exit.

Commands:
  discover  All Discovered potential peerings
  generate  Generate rendered templates using the found...
  pinder    Request a right swipe or check the status of...
```

# Examples
```
./peerme.py discover --help
./peerme.py generate --help

./peerme.py -s pdbsql discover -d 32934
./peerme.py -s pdbsql discover -i LINX # -i : not implemented
./peerme.py -s pdbsql generate -i LINX -t generic.template  # -i :not implemented
./peerme.py -s pdbsql generate -d 15169 -t generic.template


./peerme.py -s pdbapi discover -d 32934
./peerme.py -s pdbapi discover -i FranceIX-MRS # -i :not implemented
./peerme.py -s pdbapi generate -i AMS-IX # -i :not implemented
./peerme.py -s pdbapi generate -d 15169 -t ios.template

./peerme.py -s euroix --refresh-data
./peerme.py -s euroix discover -d 32934
./peerme.py -s euroix discover -i FranceIX-MRS
./peerme.py -s euroix discover -d 8218 -i FranceIX-PAR
./peerme.py -s euroix generate -i FranceIX-PAR -t ios-xr.template
./peerme.py -s euroix generate -d 8218 -i FranceIX-PAR -t ios.template
./peerme.py -s euroix generate -d 15169 -t junos.template

```

~/.peerme.conf
```
[peerme]
#set your ASN here
my_asn=32934
```

# Dev Instructions
## Mac OS X
* Get Brew: http://brew.sh/
* brew install git python3
* pip3 install aiomysql click jinja2 aiohttp

## Ubuntu >= 16.10
* sudo apt install python3-pip git
* pip3 install aiomysql click jinja2 aiohttp

# Feedback
This tool was created @ RIPE 73 Hackathon by:
* Cooper Lees <me@cooperlees.com>
* James Paussa <james@paussa.net>
* Arnaud Fenioux <peerme@afenioux.fr>

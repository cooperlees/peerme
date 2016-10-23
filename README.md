# peerme
Tool to discover and generate possible peerings between Internet Autonomous Systems

# Requirements
* Python >= 3.5
* pip modules:
    * aiomysql: https://github.com/aio-libs/aiomysql
  * (if not useing PeeringDB API)
  * aiohttp: http://aiohttp.readthedocs.io/
  * click: http://click.pocoo.org/
  * jinja2: http://jinja.pocoo.org/

# Usage
```
Usage: peerme.py [OPTIONS] COMMAND [ARGS]...

  Discover and generate potential peering endpoints @ IXs

Options:
  -c, --config TEXT  Config File Location - Default: ~/.peerme.conf
  -d, --debug        Turn on verbose logging
  -h, --help         Show this message and exit.

Commands:
  discover       All Discovered potential peerings
  generate       Generate rendered templates using the found...
```

# Dev Instructions
## Mac OS X
* Get Brew: http://brew.sh/
* brew install git python3
* pip3 install aiomysql click jinja2

## Ubuntu >= 16.10
* sudo apt install python3-pip git
* pip3 install aiomysql click jinja2

# Feedback
This tool was created @ RIPE 73 by:
* Cooper Lees <me@cooperlees.com>
* James Paussa <james@paussa.net>
* Arnaud Fenioux <arnaud@afenioux.fr>

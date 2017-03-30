#!/usr/bin/env python3
#
# Made for the RIPE IXP Tools Hackathon
#
# BSD 2-Clause License
#
# Copyright (c) 2016, Cooper Lees
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from peerme import __version__
from setuptools import setup, find_packages

setup(name='peerme',
      version=__version__,
      packages=find_packages(),
      url='http://github.com/cooperlees/peerme',
      license='BSD 2-Clause',
      author='Cooper Lees',
      author_email='me@cooperlees.com',
      description='IX Peering DB based config discovery and generation tool',
      classifiers=[
          'License :: OSI Approved :: BSD License',
          'Topic :: Internet',
          'Programming Language :: Python :: 3 :: Only',
          'Intended Audience :: System Administrators',
          'Development Status :: 3 - Alpha',
      ],
      install_requires=[
          'aiohttp',
          'aiomysql >= 0.0.9',
          'click >= 5.0',
          'jinja2',
      ],
      entry_points={
          'console_scripts': [
              'peerme = peerme.main:script_entry'
          ]
      },
      include_package_data=True,
)

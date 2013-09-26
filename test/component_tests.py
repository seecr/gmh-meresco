#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
from os import system
from sys import path
system('find .. -name "*.pyc" | xargs rm -f')

from glob import glob
for p in glob('../deps.d/*'):
    path.insert(0, p)

path.insert(0, '..')

from unittest import main

from storagesplittest import StorageSplitTest
from filterpartnamestest import FilterPartNamesTest
from knawlongtest import KNAWLongTest
from knawlong2shorttest import KNAWLong2ShortTest
from nod2shorttest import NOD2ShortTest


if __name__ == '__main__':
    try:
        main()
    finally:
        system('find .. -name "*.pyc" | xargs rm -f')

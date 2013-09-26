#!/bin/bash

USR="arnoudj"
if [ "x$1" != "x" ] ; then
    USR="$1"
fi

svn export --force "svn+ssh://$USR@tnarcis01.bureau.knaw.nl/var/svn/meresco/trunk/narcis" /home/meresco/meresco_server
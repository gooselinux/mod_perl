#!/bin/sh

/usr/lib/rpm/perl.prov $* | \
    sed -e '/perl(warnings)/d' \
        -e '/HTTP::Request::Common)/d'


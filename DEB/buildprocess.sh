#!/bin/bash

PATRONI_VERSION=1.4.3

set -ex

cd $(dirname $0)
curl -L https://github.com/zalando/patroni/archive/v${PATRONI_VERSION}.tar.gz -o patroni_${PATRONI_VERSION}.orig.tar.gz
tar -xzf patroni_${PATRONI_VERSION}.orig.tar.gz
cp -r debian/ patroni-${PATRONI_VERSION}
cd patroni-${PATRONI_VERSION}

debuild -us -uc

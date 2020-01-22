#!/bin/bash

PATRONI_VERSION=1.6.3

set -ex

cd $(dirname $0)
curl -L https://github.com/zalando/patroni/archive/v${PATRONI_VERSION}.tar.gz -o patroni_${PATRONI_VERSION}.orig.tar.gz
tar -xzf patroni_${PATRONI_VERSION}.orig.tar.gz
cp -r debian/ patroni-${PATRONI_VERSION}
cd patroni-${PATRONI_VERSION}

debuild -us -uc

export PATH=/opt/go/bin:$PATH
mkdir -p /build-tmp/gopath
export GOPATH=/build-tmp/gopath
go get github.com/cybertec-postgresql/vip-manager
cd /build-tmp/gopath/src/github.com/cybertec-postgresql/vip-manager/
make vip-manager
make package
cp vip-manager*.deb /debian-build/

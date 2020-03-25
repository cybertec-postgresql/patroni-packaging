#!/bin/sh

set -e

mkdir -p /root/rpmbuild/SOURCES
tar -czf /root/rpmbuild/SOURCES/patroni-customizations.tar.gz patroni.2.service patroni-watchdog.service postgres-telia.yml 
cp patches/*.patch /root/rpmbuild/SOURCES/
rpmbuild --rpmfcdebug -bb patroni.spec
mkdir -p rpms
cp /root/rpmbuild/RPMS/x86_64/patroni-*.rpm rpms/
if [ -n "$USER_ID" ]; then
    chown -R $USER_ID:$USER_ID rpms
fi

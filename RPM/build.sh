#!/bin/sh
mkdir -p /root/rpmbuild/SOURCES
tar -czf /root/rpmbuild/SOURCES/patroni-customizations.tar.gz patroni.2.service patroni-watchdog.service postgres-telia.yml 
cp patches/*.patch /root/rpmbuild/SOURCES/
curl -L https://github.com/zalando/patroni/archive/v1.6.3.tar.gz -o /root/rpmbuild/SOURCES/patroni-1.6.3.tar.gz
rpmbuild --rpmfcdebug -bb patroni.spec
mkdir -p rpms
cp /root/rpmbuild/RPMS/x86_64/patroni-*.rpm rpms/

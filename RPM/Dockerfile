FROM centos:7
RUN yum install -y rpm-build python-virtualenv prelink libyaml-devel gcc
WORKDIR /patroni-packaging
ENTRYPOINT ["/patroni-packaging/build.sh"]

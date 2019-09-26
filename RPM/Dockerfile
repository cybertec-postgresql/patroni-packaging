FROM centos:7
RUN yum install epel-release -y
RUN yum install -y rpm-build python36 python36-pip python36-virtualenv python36-psycopg2 prelink libyaml-devel gcc
WORKDIR /patroni-packaging
ENTRYPOINT ["/patroni-packaging/build.sh"]

FROM fedora:30
RUN dnf install -y rpm-build python3 python3-pip python3-virtualenv python3-psycopg2 libyaml-devel gcc
WORKDIR /patroni-packaging
ENTRYPOINT ["/patroni-packaging/fc30.build.sh"]

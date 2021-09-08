# This project is now deprecated!

Since [postgresql.org](https://www.postgresql.org/download/) provides [packaging](https://git.postgresql.org/gitweb/?p=pgrpms.git;a=blob;f=rpm/redhat/master/common/patroni/master/patroni.spec) for patroni on most distributions, we feel that we should not work on solving the same things in different ways. Thus we'll be deprecating this repository and the packages.

Please check [this document](package_migration.md) for migration steps.


# patroni-packaging

This project packages patroni, along with all necessary libs that aren't easily available as packages themselves.

You're probably looking for prebuilt packages, right? Then head over to the releases and download the newest version there!

## building the packages yourself

> you'll need docker installed and running

1. navigate to the `DEB` or `RPM` directory (depending of what you'd like to build).
2. execute `make docker-image` to generate a custom docker image based on either debian or centos, within which the package will be built.
3. execute `make package` to build the package. (The Debian side of things will also build vip-manager.) This may take some time, as all necessary python libraries are installed into a virtualenv, which is then packaged.
4. If you're building .debs, the packages will be in the `DEB` directory at the end of the build process. On the other hand, after building .rpms, the package will reside in the `RPM/rpms` directory.

## dependencies of the produced packages

### rpm

You'll need to install the EPEL repositories, which is the only straight forward way to get psycopg2 in a version newer than 2.5.4 (centos 7 repos only provide 2.5.1), which is a requirement of patroni.

> Due to the fact that the python packages on fedora are named `python3-something`, the packages produced by centos won't work currently, as they require `python36-something`.

### deb

Haven't tested yet. probably `python-psycopg2` will suffice. Can probably be automatically installed after apt has finished the dependency check.

> The deb packages are still packaged with python2! 

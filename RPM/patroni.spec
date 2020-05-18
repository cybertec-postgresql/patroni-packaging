%define VERSION        1.6.5
# SHA256SUM of the patroni source archive
%define SRC_SHA256SUM  a72e18e901be2404831f819b4a22c4df67d5fbb013e455d22fdc352f1e171be6

%define        ENVNAME  patroni
%define        INSTALLPATH /opt/app/patroni
%define debug_package %{nil}

# Fetch remote sources
%undefine _disable_source_fetch

Name:          patroni
Version:       %{VERSION}
Release:       1.rhel7
License:       MIT
Summary:       PostgreSQL high-availability manager
Source:        https://github.com/zalando/patroni/archive/v%{version}.tar.gz
Source1:       patroni-customizations.tar.gz
Patch0:        add-sample-config.patch
Patch1:        better-startup-script.patch
BuildRoot:     %{_tmppath}/%{buildprefix}-buildroot
Requires:      python3, python3-psycopg2 >= 2.5.4, libffi, postgresql-server, libyaml
BuildRequires: prelink libyaml-devel gcc
Requires(post): %{_sbindir}/update-alternatives
Requires(postun):       %{_sbindir}/update-alternatives

%global __requires_exclude_from ^%{INSTALLPATH}/lib/python3.6/site-packages/(psycopg2/|_cffi_backend.so|_cffi_backend.cpython-36m-x86_64-linux-gnu.so|.libs_cffi_backend/libffi-.*.so.6.0.4)
%global __provides_exclude_from ^%{INSTALLPATH}/lib/python3.6/

%global __python %{__python3}

%description
Packaged version of Patroni HA manager.

%prep
# Check SHA256 sum of the fetched source
echo "%{SRC_SHA256SUM} %{SOURCE0}" | sha256sum -c -
%setup
%setup -D -T -a 1
%patch0 -p1
%patch1 -p1

%build
# remove some things
#rm -f $RPM_BUILD_ROOT/%{prefix}/*.spec

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{INSTALLPATH}
virtualenv-3 --distribute --system-site-packages $RPM_BUILD_ROOT%{INSTALLPATH}
grep -v psycopg2 requirements.txt | sed 's/kubernetes=.*/kubernetes/' > requirements-venv.txt
$RPM_BUILD_ROOT%{INSTALLPATH}/bin/pip3 install -U setuptools
$RPM_BUILD_ROOT%{INSTALLPATH}/bin/pip3 install -r requirements-venv.txt
$RPM_BUILD_ROOT%{INSTALLPATH}/bin/pip3 install --no-deps .
#rm $RPM_BUILD_ROOT%{INSTALLPATH}/lib/python3*/site-packages/consul/aio.py

rm -rf $RPM_BUILD_ROOT/usr/

virtualenv-3.6 --relocatable $RPM_BUILD_ROOT%{INSTALLPATH}
sed -i "s#$RPM_BUILD_ROOT##" $RPM_BUILD_ROOT%{INSTALLPATH}/bin/activate*

#find $(VENV_PATH) -name \*py[co] -exec rm {} \;
#find $(VENV_PATH) -name no-global-site-packages.txt -exec rm {} \;
cp -r extras/ $RPM_BUILD_ROOT%{INSTALLPATH}

mkdir -p $RPM_BUILD_ROOT/lib/systemd/system/
cp patroni.2.service $RPM_BUILD_ROOT/lib/systemd/system/patroni.service
cp patroni-watchdog.service $RPM_BUILD_ROOT/lib/systemd/system/patroni-watchdog.service

mkdir -p $RPM_BUILD_ROOT%{INSTALLPATH}/etc/
cp postgres-telia.yml $RPM_BUILD_ROOT%{INSTALLPATH}/etc/postgresql.yml.sample
chmod 0600 $RPM_BUILD_ROOT%{INSTALLPATH}/etc/postgresql.yml.sample

# undo prelinking
find $RPM_BUILD_ROOT%{INSTALLPATH}/bin/ -type f -perm /u+x,g+x -exec /usr/sbin/prelink -u {} \;
# Remove debug info containing BUILDROOT. Hopefully nobody needs to debug or profile the python modules
find $RPM_BUILD_ROOT%{INSTALLPATH}/lib/ -type f -name '*.so' -exec /usr/bin/strip -g {} \;


%post
%{_sbindir}/update-alternatives --install %{_bindir}/patroni \
  patroni %{INSTALLPATH}/bin/patroni 10 \
  --slave %{_bindir}/patronictl patroni-patronictl %{INSTALLPATH}/bin/patronictl

%postun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove patroni %{INSTALLPATH}/bin/patroni
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/app/patroni
%attr(-, postgres, postgres) /opt/app/patroni/etc
%attr(664, root, root) /lib/systemd/system/patroni.service
%attr(664, root, root) /lib/systemd/system/patroni-watchdog.service

%changelog
* Mon May 18 2020 Ants Aasma 1.6.5-1.thel7
- Update to 1.6.5

* Mon Mar 30 2020 Ants Aasma 1.6.4-2.rhel7
- Change python dependency names to python3 and python3-psycopg2

* Wed Jan 29 2020 Pavel Zhbanov 1.6.4-1.rhel7
- Update to 1.6.4

* Wed Jan 22 2020 Pavel Zhbanov 1.6.3-1.rhel7
- Update to 1.6.3

* Mon Apr 8 2019 Julian Markwort 1.6.0-1.rhel7
- Update to 1.6.0

* Mon Apr 8 2019 Ants Aasma 1.5.6-1.rhel7
- Update to 1.5.6

* Mon Apr 1 2019 Anton Patsev 1.5.5-1.rhel7
- Update to 1.5.5

* Fri Sep 21 2018 Ants Aasma 1.5.0-1.rhel7
- Update to 1.5.0

* Wed May 23 2018 Ants Aasma 1.4.4-1.rhel7
- Update to 1.4.4
- Add patronictl reinit --wait feature

* Thu May 10 2018 Ants Aasma 1.4.3-2.rhel7
- Only display service info output in pretty format.

* Tue May 8 2018 Ants Aasma  1.4.3-1.rhel7
- Update to 1.4.3

* Fri Dec 8 2017 Ants Aasma  1.3.6-1.rhel7
- Update to 1.3.6

* Sat Sep 30 2017 Ants Aasma  1.3.4-2.rhel7
- Add warning for cluster being in paused mode
- Pull in master changes up to cfdda23e


%define        ENVNAME  patroni
%define        INSTALLPATH /opt/app/patroni
%define        GIT_REVISION 660721d
Name:          patroni
Version:       1.2
Release:       0.20161207git%{GIT_REVISION}
License:       MIT
Summary:       PostgreSQL high-availability manager
Source:        $RPM_SOURCE_DIR/patroni-venv-%{GIT_REVISION}.tar.gz
BuildRoot:     %{_tmppath}/%{buildprefix}-buildroot
Requires:      /usr/bin/python2.7, python-psycopg2 >= 2.6.1, postgresql-server, libyaml
BuildRequires: prelink
Requires(post): %{_sbindir}/update-alternatives
Requires(postun):       %{_sbindir}/update-alternatives

%description
Packaged version of Patroni HA manager.

%prep
%setup -q -c -n %{name}

%build
# remove some things
#rm -f $RPM_BUILD_ROOT/%{prefix}/*.spec

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{INSTALLPATH}

mkdir -p $RPM_BUILD_ROOT/lib/systemd/system/
cp extras/startup-scripts/patroni.2.service $RPM_BUILD_ROOT/lib/systemd/system/patroni.service
cp extras/startup-scripts/patroni-watchdog.service $RPM_BUILD_ROOT/lib/systemd/system/patroni-watchdog.service

mkdir -p $RPM_BUILD_ROOT%{INSTALLPATH}/etc/
cp extras/postgresql.yml.sample $RPM_BUILD_ROOT%{INSTALLPATH}/etc/
chmod 0600 $RPM_BUILD_ROOT%{INSTALLPATH}/etc/postgresql.yml.sample

mv bin include lib lib64 pip-selfcheck.json $RPM_BUILD_ROOT%{INSTALLPATH}
# undo prelinking
find $RPM_BUILD_ROOT%{INSTALLPATH}/bin/ -type f -perm /u+x,g+x -exec /usr/sbin/prelink -u {} \;
# remove rpath from build
#chrpath -d $RPM_BUILD_ROOT/opt/pyenv/%{ENVNAME}/bin/uwsgi
# re-point the lib64 symlink - not needed on newer virtualenv
#rm $RPM_BUILD_ROOT/opt/pyenv/%{ENVNAME}/lib64
#ln -sf /opt/pyenv/%{ENVNAME}/lib $RPM_BUILD_ROOT/opt/pyenv/%{ENVNAME}/lib64

# Remove aio implementation that is broken in Python 2. Stops bytecode compilation otherwise.
rm $RPM_BUILD_ROOT%{INSTALLPATH}/lib/python2.7/site-packages/consul/aio.py


%post
%{_sbindir}/update-alternatives --install %{_bindir}/patroni \
  patroni %{INSTALLPATH}/bin/patroni 10 \
  --slave %{_bindir}/patronictl patroni-patronictl %{INSTALLPATH}/bin/patronictl

%postun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove patroni %{INSTALLPATH}/bin/patroni
fi

%clean
#rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/app/patroni
%attr(-, postgres, postgres) /opt/app/patroni/etc
%attr(664, root, root) /lib/systemd/system/patroni.service
%attr(664, root, root) /lib/systemd/system/patroni-watchdog.service

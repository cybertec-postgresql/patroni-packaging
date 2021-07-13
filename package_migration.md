# Migrating from CYBERTEC's _patroni-packaging_ RPM to postgresql.org RPM 

Since there was no Patroni package for several distributions for quite a while, CYBERTEC packaged patroni both as RPM and DEB packages and provided it here:

https://github.com/cybertec-postgresql/patroni-packaging

Since summer 2020 the Postgresql.org project provides packages for most RPM-based distributions in the newly formed "common" repository:
e.g. for EL7:

https://download.postgresql.org/pub/repos/yum/common/redhat/rhel-7-x86_64/patroni-2.0.2-2.rhel7.x86_64.rpm

For Debian-based distributions, there exist both repositories by the distributors, and postgresql.org
e.g. for Debian Buster:

https://apt.postgresql.org/pub/repos/apt/pool/main/p/patroni/patroni_2.1.0-1.pgdg100+1_all.deb
e.g. for Ubuntu 20.04:

https://apt.postgresql.org/pub/repos/apt/pool/main/p/patroni/patroni_2.1.0-1.pgdg20.04+1_all.deb

Comparing the packages by postgresql.org and CYBERTEC, there are two different approaches:
- The CYBERTEC package installs all dependencies into a Python virtualenv
- The postgresql.org package pulls in necessary dependencies via system repositories, EPEL, or from the postgresql.org repository itself, in some cases.

The former approach means that patroni is unlikely to be influenced by other updates happening on the system. At the same time, this makes the package very big and difficult to maintain.

CYBERTEC would rather move the resources invested into helping to improve patroni and the postgresql.org packagin directly.
As a result, we are deprecating this package, and recommend everybody switches to the postgresql.org alternative.


## Migration abstract

1. Check what is running your patroni instances
    - from a service file installed with the RPM package (`/usr/lib/systemd/system/patroni.service`)?
    - from a custom systemd service file (e.g. postfixed with a cluster name `/usr/lib/systemd/system/patroni_cluster123.service`)?
2. Check where the config file used by patroni is located
    - in the location where the RPM package's systemd service file expects it (`/opt/app/patroni/etc/postgresql.yml`)? 
    - in a custom location, e.g. `/etc/patroni/config.yml`, `/etc/patroni_cluster123/config.yml`, `/etc/patroni/postgresql.yml`, `/etc/patroni/patroni.yml` - this would need to be referenced in the currently used systemd service!
3. Create a backup of the service files and config files (from all cluster members!) Also record all privileges for files and which user is used to run patroni inside of the service.
4. Pause the patroni cluster: `patronictl -c /some/path/config.yml pause`
5. Stop the service that is running patroni. Make sure that your service only stops patroni (`KillMode=process`), and not postgres!
5. uninstall the patroni RPM
6. install the new patroni RPM
7. depending on your preference, adapt the service file installed by the new RPM, move the config file into the expected location, or create a new custom service.
8. start and enable the new service. Make sure that the default service is disabled when using a custom service.
9. check the cluster state using `patronictl -c /some/path/config.yml list`
10. when the cluster member show up as "running" in the previous step's output, you can resume patroni: `patronictl -c /some/path/config.yml resume`

## Migration on a vanilla EL7 machine.

The package patroni-1.6.5-1.rhel7.x86_64.rpm packaged by CYBERTEC was installed:

<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# yum list installed | grep patroni
patroni.x86_64                       1.6.5-1.rhel7                  @/patroni-1.6.5-1
```

</p>
</details>

The service file installed by the package was used as-is:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# systemctl cat patroni
# /usr/lib/systemd/system/patroni.service
# It's not recommended to modify this file in-place, because it will be
# overwritten during package upgrades.  If you want to customize, the
# best way is to create a file "/etc/systemd/system/patroni.service",
# containing
#       .include /lib/systemd/system/patroni.service
#       Environment=PATRONI_CONFIG_LOCATION=...
# For more info about custom unit files, see
# http://fedoraproject.org/wiki/Systemd#How_do_I_customize_a_unit_file.2F_add_a_custom_unit_file.3F


[Unit]
Description=PostgreSQL high-availability manager
After=syslog.target
# Patroni needs to shut down before network interfaces. According to SystemD documentation
# specifying network.target should be sufficient, but experiments show that this is not the case.
After=network-online.target

[Service]
Type=simple

User=postgres
Group=postgres

# Location of Patroni configuration
Environment=PATRONI_CONFIG_LOCATION=/opt/app/patroni/etc/postgresql.yml

# Disable OOM kill on the postmaster
OOMScoreAdjust=-1000

ExecStart=/opt/app/patroni/bin/patroni ${PATRONI_CONFIG_LOCATION}
ExecReload=/bin/kill -HUP $MAINPID

# Give a reasonable amount of time for the server to start up/shut down
TimeoutSec=30
TimeoutStopSec=120s

# only kill the patroni process, not it's children, so it will gracefully stop postgres
KillSignal=SIGINT
KillMode=process

[Install]
WantedBy=multi-user.target
```

</p>
</details>

A cluster was configured using the config file location (`/opt/app/patroni/etc/postgresql.yml`) 
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# stat /opt/app/patroni/etc/postgresql.yml
  File: ‘/opt/app/patroni/etc/postgresql.yml’
  Size: 2170      	Blocks: 8          IO Block: 4096   regular file
Device: fd00h/64768d	Inode: 829634      Links: 1
Access: (0660/-rw-rw----)  Uid: (   26/postgres)   Gid: (   26/postgres)
Context: system_u:object_r:usr_t:s0
Access: 2021-07-13 13:30:22.845581386 +0000
Modify: 2021-07-13 13:30:05.796139000 +0000
Change: 2021-07-13 13:30:06.071554673 +0000
 Birth: -
```

</p>
</details>

referenced by the RPM package's systemd service file.
This is the running service:

<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# systemctl status patroni
● patroni.service - PostgreSQL high-availability manager
   Loaded: loaded (/usr/lib/systemd/system/patroni.service; disabled; vendor preset: disabled)
   Active: active (running) since Tue 2021-07-13 13:30:51 UTC; 1min 35s ago
 Main PID: 5502 (python3.6)
   CGroup: /system.slice/patroni.service
           ├─5502 python3.6 /opt/app/patroni/bin/patroni /opt/app/patroni/etc/postgresql.yml
           ├─5527 /usr/pgsql-12/bin/postgres -D /data/pgsql/12/data_cluster2 --config-file=/data/pgsql/12/data_cluster2/postgresql.conf --l...
           ├─5529 postgres: cluster2: logger   
           ├─5532 postgres: cluster2: checkpointer   
           ├─5533 postgres: cluster2: background writer   
           ├─5534 postgres: cluster2: walwriter   
           ├─5535 postgres: cluster2: autovacuum launcher   
           ├─5536 postgres: cluster2: stats collector   
           ├─5537 postgres: cluster2: logical replication launcher   
           ├─5540 postgres: cluster2: postgres postgres 127.0.0.1(38986) idle
           └─5565 postgres: cluster2: walsender replicator 192.168.178.247(60802) streaming 0/3000060

Jul 13 13:31:43 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:31:43,147 INFO: Lock owner: centos7-node-1; I am centos7-node-1
Jul 13 13:31:43 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:31:43,155 INFO: no action.  i am the leader with the lock
Jul 13 13:31:53 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:31:53,147 INFO: Lock owner: centos7-node-1; I am centos7-node-1
Jul 13 13:31:53 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:31:53,157 INFO: no action.  i am the leader with the lock
Jul 13 13:32:03 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:03,147 INFO: Lock owner: centos7-node-1; I am centos7-node-1
Jul 13 13:32:03 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:03,156 INFO: no action.  i am the leader with the lock
Jul 13 13:32:13 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:13,146 INFO: Lock owner: centos7-node-1; I am centos7-node-1
Jul 13 13:32:13 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:13,156 INFO: no action.  i am the leader with the lock
Jul 13 13:32:23 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:23,160 INFO: Lock owner: centos7-node-1; I am centos7-node-1
Jul 13 13:32:23 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:23,167 INFO: no action.  i am the leader with the lock
```

</p>
</details>

The cluster consists of a primary and a replica, both are currently running:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# patronictl -c /opt/app/patroni/etc/postgresql.yml list
+ Cluster: cluster2 (6984403026804426127) --+---------+----+-----------+
|     Member     |       Host      |  Role  |  State  | TL | Lag in MB |
+----------------+-----------------+--------+---------+----+-----------+
| centos7-node-1 | 192.168.178.246 | Leader | running |  1 |           |
| centos7-node-2 | 192.168.178.247 |        | running |  1 |         0 |
+----------------+-----------------+--------+---------+----+-----------+
```

</p>
</details>

Let's pause the cluster management:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# patronictl -c /opt/app/patroni/etc/postgresql.yml pause
Success: cluster management is paused
[root@centos7-node-1 ~]# patronictl -c /opt/app/patroni/etc/postgresql.yml list
+ Cluster: cluster2 (6984403026804426127) --+---------+----+-----------+
|     Member     |       Host      |  Role  |  State  | TL | Lag in MB |
+----------------+-----------------+--------+---------+----+-----------+
| centos7-node-1 | 192.168.178.246 | Leader | running |  1 |           |
| centos7-node-2 | 192.168.178.247 |        | running |  1 |         0 |
+----------------+-----------------+--------+---------+----+-----------+
 Maintenance mode: on
```

</p>
</details>

Stop the service:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# systemctl stop patroni
[root@centos7-node-1 ~]# systemctl status patroni
● patroni.service - PostgreSQL high-availability manager
   Loaded: loaded (/usr/lib/systemd/system/patroni.service; disabled; vendor preset: disabled)
   Active: inactive (dead) since Tue 2021-07-13 13:32:53 UTC; 1min 20s ago
  Process: 5502 ExecStart=/opt/app/patroni/bin/patroni ${PATRONI_CONFIG_LOCATION} (code=exited, status=0/SUCCESS)
 Main PID: 5502 (code=exited, status=0/SUCCESS)
   CGroup: /system.slice/patroni.service
           ├─5527 /usr/pgsql-12/bin/postgres -D /data/pgsql/12/data_cluster2 --config-file=/data/pgsql/12/data_cluster2/postgresql.conf --l...
           ├─5529 postgres: cluster2: logger   
           ├─5532 postgres: cluster2: checkpointer   
           ├─5533 postgres: cluster2: background writer   
           ├─5534 postgres: cluster2: walwriter   
           ├─5535 postgres: cluster2: autovacuum launcher   
           ├─5536 postgres: cluster2: stats collector   
           ├─5537 postgres: cluster2: logical replication launcher   
           └─5565 postgres: cluster2: walsender replicator 192.168.178.247(60802) streaming 0/3000060

Jul 13 13:32:33 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:33,146 INFO: Lock owner: centos7-node-1; I am centos7-node-1
Jul 13 13:32:33 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:33,152 INFO: no action.  i am the leader with the lock
Jul 13 13:32:43 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:43,146 INFO: Lock owner: centos7-node-1; I am centos7-node-1
Jul 13 13:32:43 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:43,153 INFO: no action.  i am the leader with the lock
Jul 13 13:32:46 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:46,359 INFO: Lock owner: centos7-node-1; I am centos7-node-1
Jul 13 13:32:46 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:46,368 INFO: PAUSE: no action.  i am the leader with the lock
Jul 13 13:32:46 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:46,373 INFO: No PostgreSQL configuration items changed, nothing to reload.
Jul 13 13:32:53 centos7-node-1.fritz.box systemd[1]: Stopping PostgreSQL high-availability manager...
Jul 13 13:32:53 centos7-node-1.fritz.box patroni[5502]: 2021-07-13 13:32:53,910 INFO: Leader key is not deleted and Postgresql is not stopped due paused state
Jul 13 13:32:53 centos7-node-1.fritz.box systemd[1]: Stopped PostgreSQL high-availability manager.
```

</p>
</details>

The database should continue running:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# ps -ef | grep bin/postgres
postgres  5527     1  0 13:30 ?        00:00:00 /usr/pgsql-12/bin/postgres -D /data/pgsql/12/data_cluster2 --config-file=/data/pgsql/12/data_cluster2/postgresql.conf --listen_addresses=0.0.0.0 --port=5432 --cluster_name=cluster2 --wal_level=replica --hot_standby=on --max_connections=100 --max_wal_senders=10 --max_prepared_transactions=0 --max_locks_per_transaction=64 --track_commit_timestamp=off --max_replication_slots=10 --max_worker_processes=8 --wal_log_hints=on
root      5616  5179  0 13:34 pts/0    00:00:00 grep --color=auto bin/postgres
```

</p>
</details>

After the member key has expired in the DCS, the stopped instance will no longer show up in patronictl list:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# patronictl -c /opt/app/patroni/etc/postgresql.yml list
+ Cluster: cluster2 (6984403026804426127) +---------+----+-----------+
|     Member     |       Host      | Role |  State  | TL | Lag in MB |
+----------------+-----------------+------+---------+----+-----------+
| centos7-node-2 | 192.168.178.247 |      | running |  1 |         0 |
+----------------+-----------------+------+---------+----+-----------+
 Maintenance mode: on
```

</p>
</details>

Let's uninstall the RPM:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# yum remove patroni-1.6.5-1.rhel7.x86_64
Loaded plugins: fastestmirror
Resolving Dependencies
--> Running transaction check
---> Package patroni.x86_64 0:1.6.5-1.rhel7 will be erased
--> Finished Dependency Resolution

Dependencies Resolved

==============================================================================================================================================
 Package                       Arch                         Version                             Repository                               Size
==============================================================================================================================================
Removing:
 patroni                       x86_64                       1.6.5-1.rhel7                       @/patroni-1.6.5-1                        76 M

Transaction Summary
==============================================================================================================================================
Remove  1 Package

Installed size: 76 M
Is this ok [y/N]: y
Downloading packages:
Running transaction check
Running transaction test
Transaction test succeeded
Running transaction
  Erasing    : patroni-1.6.5-1.rhel7.x86_64                                                                                               1/1 
  Verifying  : patroni-1.6.5-1.rhel7.x86_64                                                                                               1/1 

Removed:
  patroni.x86_64 0:1.6.5-1.rhel7                                                                                                              

Complete!
```

</p>
</details>

Install the new package:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# yum install patroni-etcd
Loaded plugins: fastestmirror
Loading mirror speeds from cached hostfile
epel/x86_64/metalink                                                                                                   |  29 kB  00:00:00     
 * base: mirror.23media.com
 * epel: mirror.23media.com
 * extras: ftp.plusline.net
 * updates: ftp.rz.uni-frankfurt.de
base                                                                                                                   | 3.6 kB  00:00:00     
extras                                                                                                                 | 2.9 kB  00:00:00     
pgdg-common/7/x86_64/signature                                                                                         |  198 B  00:00:00     
pgdg-common/7/x86_64/signature                                                                                         | 2.9 kB  00:00:00 !!! 
pgdg10/7/x86_64/signature                                                                                              |  198 B  00:00:00     
pgdg10/7/x86_64/signature                                                                                              | 3.6 kB  00:00:00 !!! 
pgdg11/7/x86_64/signature                                                                                              |  198 B  00:00:00     
pgdg11/7/x86_64/signature                                                                                              | 3.6 kB  00:00:00 !!! 
pgdg12/7/x86_64/signature                                                                                              |  198 B  00:00:00     
pgdg12/7/x86_64/signature                                                                                              | 3.6 kB  00:00:00 !!! 
pgdg13/7/x86_64/signature                                                                                              |  198 B  00:00:00     
pgdg13/7/x86_64/signature                                                                                              | 3.6 kB  00:00:00 !!! 
pgdg96/7/x86_64/signature                                                                                              |  198 B  00:00:00     
pgdg96/7/x86_64/signature                                                                                              | 3.6 kB  00:00:00 !!! 
updates                                                                                                                | 2.9 kB  00:00:00     
Resolving Dependencies
--> Running transaction check
---> Package patroni-etcd.x86_64 0:2.1.0-1.rhel7 will be installed
--> Processing Dependency: patroni(x86-64) = 2.1.0-1.rhel7 for package: patroni-etcd-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python3-etcd >= 0.4.3 for package: patroni-etcd-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python36-urllib3 for package: patroni-etcd-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python36-dns for package: patroni-etcd-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python36-certifi for package: patroni-etcd-2.1.0-1.rhel7.x86_64
--> Running transaction check
---> Package patroni.x86_64 0:2.1.0-1.rhel7 will be installed
--> Processing Dependency: python36-six >= 1.7 for package: patroni-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python36-prettytable >= 0.7 for package: patroni-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python36-click >= 4.1 for package: patroni-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python3-ydiff >= 1.2 for package: patroni-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python3-psutil >= 2.0.0 for package: patroni-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python36-dateutil for package: patroni-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python36-PyYAML for package: patroni-2.1.0-1.rhel7.x86_64
--> Processing Dependency: python3-cdiff for package: patroni-2.1.0-1.rhel7.x86_64
---> Package python3-etcd.noarch 0:0.4.5-20.rhel7 will be installed
---> Package python36-certifi.noarch 0:2018.10.15-5.el7 will be installed
---> Package python36-dns.noarch 0:1.16.0-1.el7 will be installed
--> Processing Dependency: python36-crypto for package: python36-dns-1.16.0-1.el7.noarch
---> Package python36-urllib3.noarch 0:1.25.6-2.el7 will be installed
--> Processing Dependency: python36-pysocks for package: python36-urllib3-1.25.6-2.el7.noarch
--> Running transaction check
---> Package python3-cdiff.noarch 0:1.0-1.rhel7 will be installed
---> Package python3-ydiff.noarch 0:1.2-10.rhel7 will be installed
---> Package python36-PyYAML.x86_64 0:3.13-1.el7 will be installed
---> Package python36-click.noarch 0:6.7-8.el7 will be installed
---> Package python36-crypto.x86_64 0:2.6.1-16.el7 will be installed
--> Processing Dependency: libtomcrypt.so.0()(64bit) for package: python36-crypto-2.6.1-16.el7.x86_64
---> Package python36-dateutil.noarch 1:2.4.2-5.el7 will be installed
---> Package python36-prettytable.noarch 0:0.7.2-19.el7 will be installed
---> Package python36-psutil.x86_64 0:5.6.7-1.el7 will be installed
---> Package python36-pysocks.noarch 0:1.6.8-7.el7 will be installed
---> Package python36-six.noarch 0:1.14.0-3.el7 will be installed
--> Running transaction check
---> Package libtomcrypt.x86_64 0:1.17-26.el7 will be installed
--> Processing Dependency: libtommath >= 0.42.0 for package: libtomcrypt-1.17-26.el7.x86_64
--> Processing Dependency: libtommath.so.0()(64bit) for package: libtomcrypt-1.17-26.el7.x86_64
--> Running transaction check
---> Package libtommath.x86_64 0:0.42.0-6.el7 will be installed
--> Finished Dependency Resolution

Dependencies Resolved

==============================================================================================================================================
 Package                                 Arch                      Version                               Repository                      Size
==============================================================================================================================================
Installing:
 patroni-etcd                            x86_64                    2.1.0-1.rhel7                         pgdg-common                    3.4 k
Installing for dependencies:
 libtomcrypt                             x86_64                    1.17-26.el7                           extras                         224 k
 libtommath                              x86_64                    0.42.0-6.el7                          extras                          36 k
 patroni                                 x86_64                    2.1.0-1.rhel7                         pgdg-common                    851 k
 python3-cdiff                           noarch                    1.0-1.rhel7                           pgdg-common                     25 k
 python3-etcd                            noarch                    0.4.5-20.rhel7                        pgdg-common                     77 k
 python3-ydiff                           noarch                    1.2-10.rhel7                          pgdg-common                     26 k
 python36-PyYAML                         x86_64                    3.13-1.el7                            epel                           149 k
 python36-certifi                        noarch                    2018.10.15-5.el7                      epel                            13 k
 python36-click                          noarch                    6.7-8.el7                             epel                           127 k
 python36-crypto                         x86_64                    2.6.1-16.el7                          epel                           487 k
 python36-dateutil                       noarch                    1:2.4.2-5.el7                         epel                            81 k
 python36-dns                            noarch                    1.16.0-1.el7                          epel                           248 k
 python36-prettytable                    noarch                    0.7.2-19.el7                          epel                            41 k
 python36-psutil                         x86_64                    5.6.7-1.el7                           epel                           395 k
 python36-pysocks                        noarch                    1.6.8-7.el7                           epel                            30 k
 python36-six                            noarch                    1.14.0-3.el7                          epel                            34 k
 python36-urllib3                        noarch                    1.25.6-2.el7                          epel                           178 k

Transaction Summary
==============================================================================================================================================
Install  1 Package (+17 Dependent packages)

Total download size: 3.0 M
Installed size: 13 M
Is this ok [y/d/N]: y
Downloading packages:
(1/18): libtommath-0.42.0-6.el7.x86_64.rpm                                                                             |  36 kB  00:00:00     
(2/18): libtomcrypt-1.17-26.el7.x86_64.rpm                                                                             | 224 kB  00:00:00     
(3/18): patroni-etcd-2.1.0-1.rhel7.x86_64.rpm                                                                          | 3.4 kB  00:00:00     
(4/18): python3-cdiff-1.0-1.rhel7.noarch.rpm                                                                           |  25 kB  00:00:00     
(5/18): patroni-2.1.0-1.rhel7.x86_64.rpm                                                                               | 851 kB  00:00:00     
(6/18): python3-etcd-0.4.5-20.rhel7.noarch.rpm                                                                         |  77 kB  00:00:00     
(7/18): python3-ydiff-1.2-10.rhel7.noarch.rpm                                                                          |  26 kB  00:00:00     
(8/18): python36-PyYAML-3.13-1.el7.x86_64.rpm                                                                          | 149 kB  00:00:00     
(9/18): python36-certifi-2018.10.15-5.el7.noarch.rpm                                                                   |  13 kB  00:00:00     
(10/18): python36-click-6.7-8.el7.noarch.rpm                                                                           | 127 kB  00:00:00     
(11/18): python36-crypto-2.6.1-16.el7.x86_64.rpm                                                                       | 487 kB  00:00:00     
(12/18): python36-dateutil-2.4.2-5.el7.noarch.rpm                                                                      |  81 kB  00:00:00     
(13/18): python36-dns-1.16.0-1.el7.noarch.rpm                                                                          | 248 kB  00:00:00     
(14/18): python36-prettytable-0.7.2-19.el7.noarch.rpm                                                                  |  41 kB  00:00:00     
(15/18): python36-psutil-5.6.7-1.el7.x86_64.rpm                                                                        | 395 kB  00:00:00     
(16/18): python36-pysocks-1.6.8-7.el7.noarch.rpm                                                                       |  30 kB  00:00:00     
(17/18): python36-six-1.14.0-3.el7.noarch.rpm                                                                          |  34 kB  00:00:00     
(18/18): python36-urllib3-1.25.6-2.el7.noarch.rpm                                                                      | 178 kB  00:00:00     
----------------------------------------------------------------------------------------------------------------------------------------------
Total                                                                                                         2.8 MB/s | 3.0 MB  00:00:01     
Running transaction check
Running transaction test
Transaction test succeeded
Running transaction
  Installing : python36-six-1.14.0-3.el7.noarch                                                                                          1/18 
  Installing : 1:python36-dateutil-2.4.2-5.el7.noarch                                                                                    2/18 
  Installing : python3-cdiff-1.0-1.rhel7.noarch                                                                                          3/18 
  Installing : python3-ydiff-1.2-10.rhel7.noarch                                                                                         4/18 
  Installing : python36-psutil-5.6.7-1.el7.x86_64                                                                                        5/18 
  Installing : python36-certifi-2018.10.15-5.el7.noarch                                                                                  6/18 
  Installing : python36-PyYAML-3.13-1.el7.x86_64                                                                                         7/18 
  Installing : python36-click-6.7-8.el7.noarch                                                                                           8/18 
  Installing : python36-pysocks-1.6.8-7.el7.noarch                                                                                       9/18 
  Installing : python36-urllib3-1.25.6-2.el7.noarch                                                                                     10/18 
  Installing : python36-prettytable-0.7.2-19.el7.noarch                                                                                 11/18 
  Installing : patroni-2.1.0-1.rhel7.x86_64                                                                                             12/18 
  Installing : libtommath-0.42.0-6.el7.x86_64                                                                                           13/18 
  Installing : libtomcrypt-1.17-26.el7.x86_64                                                                                           14/18 
  Installing : python36-crypto-2.6.1-16.el7.x86_64                                                                                      15/18 
  Installing : python36-dns-1.16.0-1.el7.noarch                                                                                         16/18 
  Installing : python3-etcd-0.4.5-20.rhel7.noarch                                                                                       17/18 
  Installing : patroni-etcd-2.1.0-1.rhel7.x86_64                                                                                        18/18 
  Verifying  : python3-etcd-0.4.5-20.rhel7.noarch                                                                                        1/18 
  Verifying  : python36-dns-1.16.0-1.el7.noarch                                                                                          2/18 
  Verifying  : libtommath-0.42.0-6.el7.x86_64                                                                                            3/18 
  Verifying  : python36-prettytable-0.7.2-19.el7.noarch                                                                                  4/18 
  Verifying  : python36-pysocks-1.6.8-7.el7.noarch                                                                                       5/18 
  Verifying  : python36-click-6.7-8.el7.noarch                                                                                           6/18 
  Verifying  : python36-PyYAML-3.13-1.el7.x86_64                                                                                         7/18 
  Verifying  : 1:python36-dateutil-2.4.2-5.el7.noarch                                                                                    8/18 
  Verifying  : patroni-2.1.0-1.rhel7.x86_64                                                                                              9/18 
  Verifying  : python36-crypto-2.6.1-16.el7.x86_64                                                                                      10/18 
  Verifying  : python36-certifi-2018.10.15-5.el7.noarch                                                                                 11/18 
  Verifying  : python36-urllib3-1.25.6-2.el7.noarch                                                                                     12/18 
  Verifying  : python36-psutil-5.6.7-1.el7.x86_64                                                                                       13/18 
  Verifying  : python36-six-1.14.0-3.el7.noarch                                                                                         14/18 
  Verifying  : python3-ydiff-1.2-10.rhel7.noarch                                                                                        15/18 
  Verifying  : libtomcrypt-1.17-26.el7.x86_64                                                                                           16/18 
  Verifying  : python3-cdiff-1.0-1.rhel7.noarch                                                                                         17/18 
  Verifying  : patroni-etcd-2.1.0-1.rhel7.x86_64                                                                                        18/18 

Installed:
  patroni-etcd.x86_64 0:2.1.0-1.rhel7                                                                                                         

Dependency Installed:
  libtomcrypt.x86_64 0:1.17-26.el7                libtommath.x86_64 0:0.42.0-6.el7                patroni.x86_64 0:2.1.0-1.rhel7            
  python3-cdiff.noarch 0:1.0-1.rhel7              python3-etcd.noarch 0:0.4.5-20.rhel7            python3-ydiff.noarch 0:1.2-10.rhel7       
  python36-PyYAML.x86_64 0:3.13-1.el7             python36-certifi.noarch 0:2018.10.15-5.el7      python36-click.noarch 0:6.7-8.el7         
  python36-crypto.x86_64 0:2.6.1-16.el7           python36-dateutil.noarch 1:2.4.2-5.el7          python36-dns.noarch 0:1.16.0-1.el7        
  python36-prettytable.noarch 0:0.7.2-19.el7      python36-psutil.x86_64 0:5.6.7-1.el7            python36-pysocks.noarch 0:1.6.8-7.el7     
  python36-six.noarch 0:1.14.0-3.el7              python36-urllib3.noarch 0:1.25.6-2.el7         

Complete!
```

</p>
</details>

The new Service file expects the configuration file to be in`/etc/patroni/patroni.yml`:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# cat /usr/lib/systemd/system/patroni.service
# It's not recommended to modify this file in-place, because it will be
# overwritten during package upgrades.  It is recommended to use systemd
# "dropin" feature;  i.e. create file with suffix .conf under
# /etc/systemd/system/patroni.service.d directory overriding the
# unit's defaults. You can also use "systemctl edit patroni"
# Look at systemd.unit(5) manual page for more info.

[Unit]
Description=Runners to orchestrate a high-availability PostgreSQL
After=syslog.target network.target

[Service]
Type=simple

User=postgres
Group=postgres

# Read in configuration file if it exists, otherwise proceed
EnvironmentFile=-/etc/patroni_env.conf

# WorkingDirectory=/var/lib/pgsql

# Where to send early-startup messages from the server
# This is normally controlled by the global default set by systemd
#StandardOutput=syslog

# Pre-commands to start watchdog device
# Uncomment if watchdog is part of your patroni setup
#ExecStartPre=-/usr/bin/sudo /sbin/modprobe softdog
#ExecStartPre=-/usr/bin/sudo /bin/chown postgres /dev/watchdog

# Start the patroni process
ExecStart=/usr/bin/patroni /etc/patroni/patroni.yml

# Send HUP to reload from patroni.yml
ExecReload=/usr/bin/kill -s HUP $MAINPID

# only kill the patroni process, not it's children, so it will gracefully stop postgres
KillMode=process

# Give a reasonable amount of time for the server to start up/shut down
TimeoutSec=30

# Do not restart the service if it crashes, we want to manually inspect database on failure
Restart=no

[Install]
WantedBy=multi-user.target
```

</p>
</details>

The easiest option will be to move the old config file to the new location:

<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# mkdir /etc/patroni
[root@centos7-node-1 ~]# mv /opt/app/patroni/etc/postgresql.yml /etc/patroni/patroni.yml
[root@centos7-node-1 ~]# stat /etc/patroni/patroni.yml
  File: ‘/etc/patroni/patroni.yml’
  Size: 2170      	Blocks: 8          IO Block: 4096   regular file
Device: fd00h/64768d	Inode: 829634      Links: 1
Access: (0660/-rw-rw----)  Uid: (   26/postgres)   Gid: (   26/postgres)
Context: system_u:object_r:usr_t:s0
Access: 2021-07-13 13:30:22.845581386 +0000
Modify: 2021-07-13 13:30:05.796139000 +0000
Change: 2021-07-13 13:39:55.873223511 +0000
 Birth: -
```

</p>
</details>

Then we can start and enable the patroni service again:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# systemctl start patroni
[root@centos7-node-1 ~]# systemctl enable patroni
Created symlink from /etc/systemd/system/multi-user.target.wants/patroni.service to /usr/lib/systemd/system/patroni.service.
```

</p>
</details>

We can see that the patroni service has started again, the replica is already connected again and the patroni instance has acquired the leader lock (while in pause mode still):
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# systemctl status patroni
● patroni.service - Runners to orchestrate a high-availability PostgreSQL
   Loaded: loaded (/usr/lib/systemd/system/patroni.service; disabled; vendor preset: disabled)
   Active: active (running) since Tue 2021-07-13 13:42:22 UTC; 4s ago
 Main PID: 5728 (patroni)
   CGroup: /system.slice/patroni.service
           ├─5527 /usr/pgsql-12/bin/postgres -D /data/pgsql/12/data_cluster2 --config-file=/data/pgsql/12/data_cluster2/postgresql.conf --l...
           ├─5529 postgres: cluster2: logger   
           ├─5532 postgres: cluster2: checkpointer   
           ├─5533 postgres: cluster2: background writer   
           ├─5534 postgres: cluster2: walwriter   
           ├─5535 postgres: cluster2: autovacuum launcher   
           ├─5536 postgres: cluster2: stats collector   
           ├─5537 postgres: cluster2: logical replication launcher   
           ├─5565 postgres: cluster2: walsender replicator 192.168.178.247(60802) streaming 0/3000148
           ├─5728 /usr/bin/python3 /usr/bin/patroni /etc/patroni/patroni.yml
           └─5735 postgres: cluster2: postgres postgres 127.0.0.1(39748) idle

Jul 13 13:42:22 centos7-node-1.fritz.box systemd[1]: Started Runners to orchestrate a high-availability PostgreSQL.
Jul 13 13:42:22 centos7-node-1.fritz.box patroni[5728]: 2021-07-13 13:42:22,956 INFO: Selected new etcd server http://192.168.178.247:2379
Jul 13 13:42:22 centos7-node-1.fritz.box patroni[5728]: 2021-07-13 13:42:22,962 INFO: No PostgreSQL configuration items changed, nothing to reload.
Jul 13 13:42:22 centos7-node-1.fritz.box patroni[5728]: 2021-07-13 13:42:22,965 INFO: establishing a new patroni connection to the postgres cluster
Jul 13 13:42:22 centos7-node-1.fritz.box patroni[5728]: 2021-07-13 13:42:22,992 INFO: PAUSE: acquired session lock as a leader
Jul 13 13:42:32 centos7-node-1.fritz.box patroni[5728]: 2021-07-13 13:42:32,994 INFO: PAUSE: no action. I am (centos7-node-1) the leader with the lock
Jul 13 13:42:33 centos7-node-1.fritz.box patroni[5728]: 2021-07-13 13:42:33,019 INFO: PAUSE: no action. I am (centos7-node-1) the leader with the lock
```

</p>
</details>

The cluster member shows up in patronictl list again:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# patronictl -c /etc/patroni/patroni.yml list
+ Cluster: cluster2 (6984403026804426127) ---+---------+----+-----------+
| Member         | Host            | Role    | State   | TL | Lag in MB |
+----------------+-----------------+---------+---------+----+-----------+
| centos7-node-1 | 192.168.178.246 | Leader  | running |  1 |           |
| centos7-node-2 | 192.168.178.247 | Replica | running |  1 |         0 |
+----------------+-----------------+---------+---------+----+-----------+
 Maintenance mode: on
```

</p>
</details>


You can now install the update on all other patroni members, taking the same steps (stopping the service, uninstalling the old and installing the new package, moving the config file, starting the patroni service again).

At the end, resume from pause mode:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# patronictl -c /etc/patroni/patroni.yml resume
Success: cluster management is resumed
[root@centos7-node-1 ~]# patronictl -c /etc/patroni/patroni.yml list
+ Cluster: cluster2 (6984403026804426127) ---+---------+----+-----------+
| Member         | Host            | Role    | State   | TL | Lag in MB |
+----------------+-----------------+---------+---------+----+-----------+
| centos7-node-1 | 192.168.178.246 | Leader  | running |  1 |           |
| centos7-node-2 | 192.168.178.247 | Replica | running |  1 |         0 |
+----------------+-----------------+---------+---------+----+-----------+
```

</p>
</details>

It is certainly possible to have different patroni versions running in the cluster at the same time:
<details><summary>show</summary>
<p>

```bash
[root@centos7-node-1 ~]# curl -s http://192.168.178.246:8008 | jq
{
  "state": "running",
  "postmaster_start_time": "2021-07-13 13:30:53.112059+00:00",
  "role": "master",
  "server_version": 120007,
  "cluster_unlocked": false,
  "xlog": {
    "location": 50332208
  },
  "timeline": 1,
  "replication": [
    {
      "usename": "replicator",
      "application_name": "centos7-node-2",
      "client_addr": "192.168.178.247",
      "state": "streaming",
      "sync_state": "async",
      "sync_priority": 0
    }
  ],
  "database_system_identifier": "6984403026804426127",
  "patroni": {
    "version": "2.1.0",
    "scope": "cluster2"
  }
}
[root@centos7-node-1 ~]# curl -s http://192.168.178.247:8008 | jq
{
  "state": "running",
  "postmaster_start_time": "2021-07-13 13:31:20.660 UTC",
  "role": "replica",
  "server_version": 120007,
  "cluster_unlocked": false,
  "xlog": {
    "received_location": 50332208,
    "replayed_location": 50332208,
    "replayed_timestamp": null,
    "paused": false
  },
  "timeline": 1,
  "database_system_identifier": "6984403026804426127",
  "patroni": {
    "version": "1.6.5",
    "scope": "cluster2"
  }
}
```

</p>
</details>


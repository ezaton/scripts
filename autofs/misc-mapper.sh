#!/bin/bash
# Defaults
SRV=nfssrv
OPTS="-rw,soft,vers=3"
BASE=/share
CONFDIR=/etc/auto.master.conf

# Create in /etc/auto.master.conf a file called ${KEY}.conf with the following settings to override:
# SRV=other_server # or can be a FQDN, or even empty
# OPTS=mount options, like "-fstype=davfs,rw,uid=1000,gid=1000" or "-rw,soft,intr,rsize=1024000,wsize=1024000" or "-fstype=cifs,uid=1000,gid=1000,username=cifsuser,password=password"
# BASE=URL Base, like (when NFS server presents) /share/temp ; or https\://mynextcloud.nextcloud.com/remote.php/webdav/ or //cifsserver/config
# KEY= If you want to override the provided local key, use it, or set it to nothing. Otherwise, do not set it. and use the original key by autofs
# SKIP_PING= -> if set, will not ping before

KEY=${1}
function obtain_info() {
  if [ -f ${CONFDIR}/${KEY}.conf ] ; then
    . ${CONFDIR}/${KEY}.conf
  fi
}

obtain_info
if [ -z "${SKIP_PING}" ] ; then
  if ! ping -W 1 -c 1 ${SRV} > /dev/null 2>&1 ; then
    exit 1
  fi
fi
echo "$OPTS $SRV:${BASE}/${KEY}" 

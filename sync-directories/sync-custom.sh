#!/bin/bash
# Using rsync to sync directories

# Variables
LOCKDIR=/dev/shm
LOGFILE=/tmp/rsync-custom.$$.log
LOGSUM=/tmp/rsync.sum.$$
SRC=/mnt/source
DST=/mnt/target
PARALLELS=5

function lock(){
	# If a lock file exists, exit with a message
	BASE64="$( echo $1 | base64 )"
	LOCKFILE=${LOCKDIR}/${BASE64}
	if [ -f ${LOCKFILE} ]; then
		echo "Lock file ${LOCKFILE} exists. If by a mistake - remove it manually"
		echo "$(date) ${SRC}/${1} is locked" >> $LOGSUM
		return 1
	else
		\rm ${LOCKFILE}.lock
		touch ${LOCKFILE}
		return 0
	fi
}

function unlock(){
	# Remove lock file
	BASE64="$( echo $1 | base64 )"
	LOCKFILE=${LOCKDIR}/${BASE64}
	rm -f ${LOCKFILE}
}

function sync(){
	echo "$(date) Starting sync of ${SRC}/${1}" >> $LOGSUM
	postlock $1
	/usr/bin/rsync --max-alloc=0 -a --human-readable --stats --delete --one-file-system -X -A ${SRC}/${1} ${DST} >> ${LOGFILE} 2>&1
	#/usr/bin/rsync -a --log-file=${LOGFILE} --human-readable --stats --delete --one-file-system --dry-run -X -A ${SRC} ${DST}
	echo "$(date) Finished sync of ${SRC}/${1}" >> $LOGSUM
	unlock ${1}
}

function show_log(){
	echo "Log file is $LOGFILE"
	echo "Sum log is $LOGSUM"
}

function prelock() {
	# Allows parallel run of rsync
	BASE64="$( echo $1 | base64 )"
        LOCKFILE=${LOCKDIR}/${BASE64}
	if [ -f ${LOCKFILE}.lock ] ; then
		return
	fi
	touch ${LOCKFILE}.lock
	SRCLIST="${SRCLIST} $1"
}

function postlock() {
	# Cleanup prelock
	BASE64="$( echo $1 | base64 )"
        LOCKFILE=${LOCKDIR}/${BASE64}
	if [ -f ${LOCKFILE}.lock ] ; then
		\rm -f ${LOCKFILE}.lock
	fi
}

### MAIN ###
COUNTER=0
CLEANLIST=""
for file in $( ls $SRC ); do
	prelock $file
done
for file in ${SRCLIST}; do
	if lock $file ; then
		sync $file &
		let COUNTER++
	fi
	if [ ${COUNTER} -ge ${PARALLELS} ] ; then
		wait -n
		let COUNTER--
	fi
done
wait
show_log

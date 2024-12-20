#!/bin/bash
# Unattended migration, run under tmux
# Using data structure like this:
# vgname:old_pv:new_pv
# Use case - a single pv move for a single VG, but for many different VGs.
# Will not handle removal of multiple PVs in a single VG.
EMAIL=reportee@mail.com
if [ ! -f ${1} ] ; then
	echo "Missing file list. Use the following syntax in the file:"
	echo "vgname:old_pv:new_pv"
	echo "Comments are ignored. Do not use spaces"
	exit 1
fi

LOG=/root/pvmove_log.txt

function abort() {
	echo "$@"
	exit 1
}

function report() {
	mail -s "Done migrating $NPV to $OPV" ${EMAIL} < /dev/null
}

function parse_list() {
	# Parse the objects
	VG=$( echo ${line} | cut -f 1 -d : )
	OPV=$( echo ${line} | cut -f 2 -d : )
	NPV=$( echo ${line} | cut -f 3 -d : )
	if [ -z "${VG}" -o -z "${NPV}" -o -z "${OPV}" ]; then
		echo "Incorrect arguments."
		exit 1
	fi
}

function add_pv() {
	# Adds the PV to the VG
	echo "$( date ) Adding PV $NPV to VG $VG" >> $LOG
	/usr/sbin/vgextend ${VG} ${NPV}
	RET=$?
	if [ ${RET} -ne 0 ] ; then
		abort "Failed to extend VG ${VG} to new PV ${NPV}"
	fi
	echo "$( date ) Done Adding PV $NPV to VG $VG" >> $LOG
	return $RET
}

function move_pv() {
	# Performs the migration
	echo "$( date ) Running pvmove on $OPV" >> $LOG
	/usr/sbin/pvmove ${OPV}
	RET=$?
	if [ ${RET} -ne 0 ] ; then
		abort "Failed to perform pvmove on ${OPV}"
	fi
	echo "$( date ) Done Running pvmove on $OPV" >> $LOG
	return $RET
}

function remove_pv() {
	# Removes the old PV from VG
	echo "$( date ) Removing PV $OPV from VG $VG" >> $LOG
	/usr/sbin/vgreduce ${VG} ${OPV}
	RET=$?
	if [ ${RET} -ne 0 ] ; then
		abort "Failed to reduce the PV ${OPV} from VG ${VG}"
	fi
	echo "$( date ) Done Removing PV $OPV from VG $VG" >> $LOG
	report
	return $RET
}


### MAIN
for line in $( cat ${1} | grep -v ^$ | grep -v \# ); do
	parse_list ${line}
	add_pv && move_pv && remove_pv
	echo "Finished moving VG ${VG}" | tee -a $LOG
done

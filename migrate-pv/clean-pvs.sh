#!/bin/sh
MPLIST=$( multipath -l| grep dm- | awk '{print $1}' | grep -v ^ps- )
for i in $MPLIST ; do echo $i ;  DISKS=$( multipath -ll ${i} | grep ready | awk '{print $3}' ); multipath -f $i && for j in ${DISKS}; do echo $j ; echo 1 > /sys/block/${j}/device/delete; done ; done


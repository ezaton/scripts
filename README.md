# Varios general-purpose scripts with nowhere else to put them
## Directories:
- pppoe-hijack: A script to capture PPPoE login information from locked routers.
- autofs: An autofs script to reduce delays when shares are inaccessible by replacing a static map with a script that includes ping command
- migrate-pv: A set of scripts to automate 'pvmove' operations while performing storage migration
- sync-directories: A script for parallel rsync of a directory, to reduce time when handling very large directories. Modify $SRC $DST and $PARALLELS according to performance and expactaions
- lmstudio-headless: A directory with systemd unit files required to enable lm-studio in a headless mode on Linux. The backend unit files used in 
https://run.tournament.org.il/running-headless-lm-studio-on-ubuntu/

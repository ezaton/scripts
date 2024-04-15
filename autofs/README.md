Dynamic autofs script to reduce inaccessible NFS mounts timeout
During autofs access, if the NFS server is unavailable, connection needs to exceed TCP timeout, which leads to long delays.
The effect is visible with GUI file browsers, which attempt to follow symlinks.

By using a program instead which preceeds the mount command with a short ping command, the timeouts are shorter.

The script needs to be set executable, and is expected to be called as a program from auto.master, like this:

/misc program:/usr/local/bin/misc-mapper.sh

The script misc-mapper.sh looks the map key in /etc/auto.master.conf/ - by looking the name of the key with a .conf suffix, and overrides
default settings as they are presented in these variables.

See the script for how, or take a look at the multiple examples placed in this repo under auto.master.conf directory.

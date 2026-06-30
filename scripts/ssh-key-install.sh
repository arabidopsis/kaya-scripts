#!/bin/bash
# should be run using sudo
source ./ssh-functions.sh

for dir in ${MOUNT}/s-*
do
	student=$(basename $dir)
    sshdir $student
done

# edit /etc/ssh/sshd_config so 
# Include /etc/ssh/sshd_config.d/*.conf
# is not commented out
rm -f /etc/ssh/sshd_config.d/perm.conf
for dir in ${MOUNT}/s-*
    student=$(basename $dir)
    sshkey $student
done
# restart server
systemctl restart sshd

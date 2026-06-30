#!/bin/bash
# should be run using sudo
source ./ssh-functions.sh

# create .ssh directory in each student directory
for dir in ${MOUNT}/s-*
do
	student=$(basename $dir)
    sshdir $student
done

# **edit** /etc/ssh/sshd_config so as
# Include /etc/ssh/sshd_config.d/*.conf
# is not commented out
rm -f /etc/ssh/sshd_config.d/perm.conf
# see ssh-keygen.sh cp public key to 
# ~/.ssh/authorized_keys for each student
for dir in ${MOUNT}/s-*
    student=$(basename $dir)
    sshkey $student
done
# restart sshd server
systemctl restart sshd

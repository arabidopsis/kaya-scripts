#!/bin/bash

MOUNT=/mnt/s-ws
# for user in ubuntu appbioadm mamun sarah nina teng
# do
#     echo "DenyUsers ${user}" >> deny-users.conf
# done

for dir in ${MOUNT}/s-*
do

	student=$(basename $dir)
    echo "DenyUsers ${student}" >> deny-users.conf

done
echo "Now Run:"
echo "sudo mv deny-users.conf /etc/ssh/sshd_config.d/"
echo "sudo systemctl restart sshd"

#!/bin/bash
# should be run using sudo
for dir in /mnt/s-ws/s-*
do
	student=$(basename $dir)
	if [ ! -d "$dir/.ssh" ] ; then
		mkdir "$dir/.ssh"
		chown $student:$student "$dir/.ssh"
	fi
done

# edit /etc/ssh/sshd_config so 
# Include /etc/ssh/sshd_config.d/*.conf
# is not commented out
rm -f /etc/ssh/sshd_config.d/perm.conf
for dir in /mnt/s-ws/s-*
    student=$(basename $dir)
    ak=$dir/.ssh/authorized_keys
    sudo cp keys/public/${student}-key.pub $ak
    sudo chmod 600 $ak
    sudo chown ${student}:${student} $ak
    sudo cat <<EOF >> /etc/ssh/sshd_config.d/perm.conf
Match user ${student}
    PasswordAuthentication no
    PubkeyAuthentication yes
EOF
done
# restart server
systemctl restart sshd

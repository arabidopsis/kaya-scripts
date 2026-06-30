MOUNT=/mnt/s-ws
KEYS=$HOME/keys
function keygen () {
	local student=$1
    ssh-keygen -t rsa -b 4096 -q -N '' -f ${KEYS}/${student}-key
    mv ${KEYS}/${student}-key ${KEYS}/private
    mv ${KEYS}/${student}-key.pub ${KEYS}/public
}

function sshdir () {
	local student=$1
    local dir=$MOUNT/$student
	if [ ! -d "$dir/.ssh" ] ; then
        echo "Creating .ssh for $student"
		mkdir "$dir/.ssh"
		chown $student:$student "$dir/.ssh"
	fi
}
function sshkey () {
	local student=$1
    local dir=${MOUNT}/$student
    ak=$dir/.ssh/authorized_keys
    sudo cp ${KEYS}/public/${student}-key.pub $ak
    sudo chmod 600 $ak
    sudo chown ${student}:${student} $ak
    sudo cat <<EOF >> /etc/ssh/sshd_config.d/perm.conf
Match user ${student}
    PasswordAuthentication no
    PubkeyAuthentication yes
EOF
}

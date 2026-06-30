MOUNT=/mnt/s-ws
function keygen () {
	local student=$1
    ssh-keygen -t rsa -b 4096 -q -N '' -f keys/${student}-key
    mv keys/${student}-key keys/private
    mv keys/${student}-key.pub keys/public
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
function sshkey() {
	local student=$1
    local dir=$MOUNT/$student
    ak=$dir/.ssh/authorized_keys
    sudo cp keys/public/${student}-key.pub $ak
    sudo chmod 600 $ak
    sudo chown ${student}:${student} $ak
    sudo cat <<EOF >> /etc/ssh/sshd_config.d/perm.conf
Match user ${student}
    PasswordAuthentication no
    PubkeyAuthentication yes
EOF
}

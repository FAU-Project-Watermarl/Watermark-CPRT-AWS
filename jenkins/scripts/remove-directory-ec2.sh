#!/bin/bash

# Show the commands and stop on any error
set -xe

# Input arguments
FOLDER=$1

# display current directory for debug purpouses in pipeline
pwd

# Retrieve EC2 ip address
newIp=$(aws ec2 describe-instances --instance-ids i-03d877e4cae11232c | grep PublicIpAddress | awk '{ print $2 }' | sed 's/.$//')
#newIp=${newI:2: -2}
newIp=${newIp//\"/}
echo $newIp

# Common SSH options for all commands:
#   -q -- quiet SSH e.g. no welcome banner
#   -o StrictHostKeyChecking -- do not show hostkey warnings
#   -o UserKnownHostsFile -- do not add host of SSH target to local known_hosts file
# In addition to those, add -T when sending multiple lines via <<EOL (heredoc text)
#SSH_SETTINGS="-q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
SSH_SETTINGS="-q -o StrictHostKeyChecking=no"

###     The following actions will executed in the ec2 instance:     ###
#######################################################################
# Display current direcotry in ec2  and list files                    #
# Move to the work directory                                          #
# Remove folder with tempprar files                                   #
#######################################################################
ssh -i '~/test2.pem' $SSH_SETTINGS -T "ubuntu@$newIp" <<EOL
set -xe
pwd
cd handle_extract/extract/
ls -la
echo 'Remove folder <$FOLDER> and its content'
rm -rf $FOLDER
EOL
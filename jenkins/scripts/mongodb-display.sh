#!/bin/bash

# Input arguments
USERNAME=$1
PASSWORD=$2

# Show the commands and stop on any error
set -xe

###     The following actions will executed in MongoDb cluster:     ###
#######################################################################
# connect to the cluster using mongosh                                #
# Select watermark database                                           #
# Print all records for uuid collection                               #
#######################################################################
mongosh "mongodb+srv://cluster0.82o4qbt.mongodb.net/" --apiVersion 1 --username $USERNAME --password $PASSWORD <<EOL
use watermark
db.uuid.find()
.exit
EOL
echo 'MongoDB connection closed'

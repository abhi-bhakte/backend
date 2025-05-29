#!/bin/bash

# Define your EC2 connection details
KEY_PATH="./GABE.pem"
USER="ubuntu"  # default for Amazon Linux. Use "ubuntu" for Ubuntu instances.
HOST="ec2-3-110-47-212.ap-south-1.compute.amazonaws.com"  # replace with your EC2 public DNS or IP

# Make sure the key has proper permissions
chmod 400 $KEY_PATH

# Connect via SSH
ssh -i $KEY_PATH $USER@$HOST

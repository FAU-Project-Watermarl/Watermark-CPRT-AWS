#!/bin/bash

# **************************************************************
# *                                                            *
# *                       AWS EC2 Server setup                 *
# *                                                            *
# **************************************************************

# Prerequisites:
#   * AWS account
#   * An Amazon EC2 key pair created
#   * AWS IAM User with programmatic key access with permission

# Security Group:
#   * Create security group
#   * Select VPC
#   * the Inbound tab, add the rules: 
#       > Add Rule, and then select SSH from the Type list.
#       > Under Source, select Custom and add IP 
#       > Select Add Rule, and then select HTTP from the Type list.
#       > Select Add Rule, and then select HTTPS from the Type list.
#       > Select Add Rule, and then select SSH from the Type list.

# Amazon EC2 instance:
#   * Open the Amazon EC2
#   * EC2 dashboard, select Launch Instance.
#   * Chose ubuntu-jammy-22.04-amd64-server-20230516 AMI(or current image)
#   * Select an existing security group previously created
#   * Launch instance

# Show the commands and stop on any error
set -xe

# Run system package updates and upgrades using 'apt' package manager.
# 'apt update': Fetches the latest package information from the repositories.
# 'apt upgrade -y': Upgrades installed packages to their latest versions, automatically answering 'yes' to any prompts.
sudo apt update && sudo apt upgrade -y

# ================================== 
#            Install ffmpeg
# ================================== 
# Install the FFmpeg multimedia framework using the 'apt' package manager.
sudo apt install ffmpeg -y

# ================================== 
#            Install Bento4
# ================================== 
# Clone the repository 'Bento4'.
git clone https://github.com/axiomatic-systems/Bento4.git

# Install CMake using the 'apt' package manager with the '-y' flag for automatic confirmation.
sudo apt install cmake -y

# Install build-essential package which includes essential tools for building packages.
sudo apt-get install build-essential -y

# Change the current directory to cmakebuild inside bento4.
cd Bento4 && mkdir cmakebuild && cd cmakebuild

# Run CMake to generate build files with the 'Release' build type.
cmake -DCMAKE_BUILD_TYPE=Release ..

# Build the project using the generated build files.
sudo make

# Install the built files into the system directories with administrative privileges.
sudo make install

# Copy the 'utils' directory from the '../Source/Python/' directory to '/usr/local/bin' .
sudo cp -r ../Source/Python/utils /usr/local/bin

# Copy the 'wrappers' directory from the '../Source/Python/' directory to '/usr/local/bin'.
sudo cp -r ../Source/Python/wrappers /usr/local/bin

# Export the path for wrappers and utils to the PATH environment variable in ~/.bashrc
echo -e "\n# Add bento4 wrappers and utils to PATH" >> ~/.bashrc
echo 'export PATH="/usr/local/bin/wrappers:$PATH"' >> ~/.bashrc
echo 'export PATH="/usr/local/bin/utils:$PATH"' >> ~/.bashrc

# Go back to home directorie
cd ~

# ================================== 
#       Watermark python logic
# ================================== 
# create directories and if already exist not print error
mkdir -p handle_extract/extract/

# Copy python logic scripts to its worker directorie 
# preserving the directory structure (-r recursive).
cp -r Watermark-CPRT-AWS/pythonExtract/. ./handle_extract/extract/

# Install Python 3 package manager (pip) and venv  with the '-y' flag for automatic confirmation.
sudo apt install python3-pip -y
sudo apt install python3.10-venv -y

# Change the current directory to handle_extract/extract/.
cd handle_extract/extract/

# Create a virtual environment using Python 3's built-in venv module.
sudo python3 -m venv env

# activate virtual enviroment
source env/bin/activate

# Install Python packages required packages for the app.
python3 -m pip install -r requirements.txt

# Go back to home directorie
cd ~

# Download the AWS CLI(command line interface) version 2 package for Linux (x86_64) 
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Install the unzip utility using the package manager (apt-get)
# Unzip the "awscliv2.zip" package.
sudo apt-get install unzip
unzip awscliv2.zip

# Install the libc6 library, groff, less package (apt-get) with superuser privileges (sudo).
sudo apt-get install libc6 -y
sudo apt-get install groff -y
sudo apt-get install less -y

# Run the installation script for AWS CLI version 2 located in the current directory.
sudo ./aws/install
# Check the version of the installed AWS CLI for debugging purposes.
aws --version

# Configure the AWS CLI with your access keys and preferred settings.
# Make sure to have the follwing info to fill
# AWS Access Key ID
# AWS Secret Access Key
# Default region name
# Default output format
aws configure


#!/bin/bash

# **************************************************************
# *                                                            *
# *                       Jenkins EC2 setup                    *
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
#       > Select Add Rule, and then select Custom TCP Rule from the Type list.
#       > Under Port Range, enter 8080.

# Amazon EC2 instance:
#   * Open the Amazon EC2
#   * EC2 dashboard, select Launch Instance.
#   * Chose debian-11-amd64-20230515-1381 AMI(or current image)
#   * Select an existing security group previously created
#   * Launch instance

# Update the package list and install chrony for time synchronization.
sudo apt-get updateb -y
sudo apt-get install -y chrony

# Check if the "Restart" option is configured in the chrony.service file, and if not, add it.
# This ensures that the chrony service restarts on failure.
grep Restart /lib/systemd/system/chrony.service || sed -i 's/\[Service\]/\[Service\]\nRestart=on-failure/' /lib/systemd/system/chrony.service
sudo grep Restart /lib/systemd/system/chrony.service || sed -i 's/\[Service\]/\[Service\]\nRestart=on-failure/' /lib/systemd/system/chrony.service

# Reload systemd manager configuration to apply the changes made to the chrony.service file.
systemctl daemon-reload

# Enable and start the chrony service
sudo systemctl daemon-reload
sudo systemctl enable chrony
sudo systemctl start chrony
sudo systemctl restart chrony

# Update the package list again
apt-get update
sudo apt-get update

# Install various packages required for Jenkins and Git.
sudo apt-get install -y     curl     nmap     python3-venv     rsync     wget
sudo apt-get install -y git
git --version

# Install the default Java Runtime Environment (JRE).
sudo apt-get install -y default-jre

# Add Jenkins repository key and repository URL to the sources list.
sudo wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
if ! grep "deb https://pkg.jenkins.io/debian binary/" /etc/apt/sources.list; then     echo "deb https://pkg.jenkins.io/debian binary/" >> /etc/apt/sources.list; fi
apt-get install -y jenkins

# Update the package list again.
sudo apt-get install -y jenkins

# Download the Jenkins repository key from the specified URL and display it on the terminal.
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key

# Download the Jenkins repository key from the specified URL and save it as /usr/share/keyrings/jenkins-keyring.asc.
# The '-fsSL' options with 'curl' stand for fail silently, follow redirects, and show progress.
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee   /usr/share/keyrings/jenkins-keyring.asc > /dev/null

# Add the Jenkins repository to the system's package sources list (/etc/apt/sources.list.d/jenkins.list).
# The Jenkins repository is marked as signed by the jenkins-keyring.asc key.
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc]   https://pkg.jenkins.io/debian-stable binary/ | sudo tee   /etc/apt/sources.list.d/jenkins.list > /dev/null

# Update the package list to fetch information about available packages from added repositories.
sudo apt-get update

# Install Jenkins from the newly added repository.
# Enable the Jenkins service to start on system boot.
# Start the Jenkins service.
sudo apt-get install jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins

# Display the initial administrative password for Jenkins.
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
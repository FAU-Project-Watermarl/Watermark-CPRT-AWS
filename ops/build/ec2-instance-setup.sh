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

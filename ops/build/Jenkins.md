# Jenkins Server installation

- [x] Prerequisites:
   * AWS account
   * An Amazon EC2 key pair created
   * AWS IAM User with programmatic key access with permission


 
- [x] Security Group:
  * Create security group
  * Select VPC
  * the Inbound tab, add the rules: 
    - Add Rule, and then select SSH from the Type list.
    - Under Source, select Custom and add IP 
    - Select Add Rule, and then select HTTP from the Type list.
    - Select Add Rule, and then select Custom TCP Rule from the Type list.
    - Under Port Range, enter 8080. 
  

- [x] Amazon EC2 instance:
   * Open the Amazon EC2
   * EC2 dashboard, select Launch Instance.
   * Chose debian-11-amd64-20230515-1381 AMI(or current image)
   * Select an existing security group previously created
   * Launch instance.  

- [X] Run `jenkins-instance.sh` script inside the jenkins ec2 instance
- [X] Make user to have AWS credential info to fill when `aws configure` is called
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region name
   - Default output format
- [X] Connect to http://<your_server_public_DNS>:8080 from your browser(AWS ec2 DNS)
- [X] Use initial password displayed at the end of the script the script or `sudo cat /var/lib/jenkins/secrets/initialAdminPassword`

![Jenkins first start](https://www.jenkins.io/doc/book/resources/tutorials/AWS/unlock_jenkins.png)

- [X]  Jenkins installation script directs you to the Customize Jenkins page. Click Install suggested plugins.
- [X] Once the installation is complete, the Create First Admin User will open. Enter your information, and then select Save and Continue.
- [X] make sure to copy the folder of scripts to /tmp/scripts adn the jenkins files to /tmp/jenkinsfiles in order to be able to access with jenkins user and also appply permission chmod +x to allow executions 

- [X] Create the corresponding pipelines from the jenkinsfile previous copied
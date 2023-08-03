# EC2 worker Server installation

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
    - Select Add Rule, and then select SSH from the Type list.
  

- [x] Amazon EC2 instance:
   * Open the Amazon EC2
   * EC2 dashboard, select Launch Instance.
   * Chose ubuntu-jammy-22.04-amd64-server-20230516 AMI(or current image)
   * Select an existing security group previously created
   * Launch instance.  

![ec2 create instance](../img/ec2.JPG)

- [X] SSh in your ec2 instance to check is working and you have ssh connection
   - `ssh -i "keyPair.pem" admin@ec2IpAddress`
- [X] Inside the ec2 machine clone the github repo
   - `git clone https://github.com/FAU-Project-Watermarl/Watermark-CPRT-AWS.git`
- [X] Run ec2-instance-setup.sh script inside the ec2 instance (this will install all need to run)
   - `bash ./Watermark-CPRT-AWS/ops/build/ec2-instance-setup.sh`
- [X] Make user to have AWS credential info to fill when `aws configure` is called
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region name
   - Default output format
   
- [X] Create MongoCredentials.env file an store credentials inside, mandatory to ruin the watermark scripts
   - `echo 'mongodb+srv://<username>:<password>@clusterID.mongodb.net/?retryWrites=true&w=majority' > handle_extract/extract/MongoCredentials.env`

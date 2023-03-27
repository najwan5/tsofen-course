Notes:
You must specify the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY inside final.tf in the docker run command.
The public key (demokey) is created on linux machine back then(id_rsa.pub), you need to create a new pair using ssh-keygen 
You must git clone the folder and cd to where final.tf is located then run:
  terraform init
  terraform apply
  terraform destroy when finishing
	
----------------------------------------------	
Description:
Upload text files to S3 buckets and convert them to PDFs on AWS EC2 using the  following technologies: 

Docker Container '\n'
Python - boto3
AWS Services: S3; Lambda; SQS; EC2, Cloudwatch,  (SNS for email notification - Optional) 
IaC - terraform
Jenkins

Step1 -
Upload text files to S3 bucket.
Lambda function will be triggered to send messages to SQS-queue with resource details(the name of the file, bucket, ...) once files are uploaded

EC2 containers will handle the message(as JSON): to identify and download the files from S3 to the ec2 and to convert these files from txt to pdf 
EC2s will read messages from SQS using boto3 and convert the files using python script on docker image
Build a docker image - based on python - (Dockerfile) with FPDF,boto3, git, python script,... 
push image to docker hub
docker build image and run this container (on local)



Step2 - IaC (Terraform)
Create a terraform file that builds the above

Step3 - CI/CD (Jenkins) - Optional
A Jenkins pipeline will be build when commiting and pushing a new change to the image 

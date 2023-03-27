terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_key_pair" "deployer" {
  key_name   = "demokey"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDEtfNScruK7I9j0QwNDYrU/A5TqPmU3TYxCrvh32i5AzG/tlgabzOCZltxeAC03LVjwrLg7csMa8O4bp3h9KTrY2X8Ok4mOMvqsemmZkdVp8wCSbFhD1Ewo9jj+67gx2qIJxgeOnINE3cvYFXLIht/v1tzZAOOroJr+G7PGQ+qUE3aAERdggwKxCN9LO3+Gyn/wCVtz2T2JnDCyJfTp7EE2H8MNpdMZUZI+SuZI0wD5PGDi1p4bAT+2xBbUoohrZMEMKNyvB5z8k2FKVuqHL3xfwisiDGmbc6+I+zuhDV/RpkgYc2xdwkx3aNNgajSfwIDw8y/RKt9GAYmNGXhqj5njRnrbrQS+e+FILhaY00Oa8a9FZT0sF/3Q/DwH+7iWLlaV+I5T8+bFu7SGYYB/v/si9hi/CUiDyjlQF8w2nUoh6sBPu7lnGAFzOzpc7cVoYGhqp0F8Q6/wriLzfHk2RmTHlIf15fbl5T0HhYDpp5UM9/GfNCi2nQMoKUQ2RSgqys="
}

resource "aws_vpc" "vpcTerraform" {
  cidr_block = "10.2.0.0/16"
  tags = {
    Name = "vpcTF"
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"]
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  key_name = aws_key_pair.deployer.key_name
  network_interface {
    network_interface_id = aws_network_interface.networkInterface.id
    device_index         = 0
  }
  tags = {
    Name = "executer"
  }
  user_data = <<EOF
#!/bin/bash
curl -sfL https://get.docker.com -o docker.sh
chmod +x docker.sh
sudo ./docker.sh
sudo usermod -aG docker ubuntu
sudo docker run -e AWS_ACCESS_KEY_ID=<> -e AWS_SECRET_ACCESS_KEY=<> -e AWS_DEFAULT_REGION=us-east-1 --name txt-pdf-app -d najwan5/txt-pdf-app:latest
EOF

}

resource "aws_network_interface" "networkInterface" {
  subnet_id   = aws_subnet.TerraformSubnet.id
  private_ips = [""]
  security_groups = [aws_security_group.forwarder.id]
  tags = {
    Name = "primary_network_interface"
  }
}

resource "aws_subnet" "TerraformSubnet" {
  vpc_id            = aws_vpc.vpcTerraform.id
  cidr_block        = "10.2.1.0/24"
  availability_zone = "us-east-1b"
  map_public_ip_on_launch = true
  depends_on = [aws_internet_gateway.gw]  
  tags = {
    Name = "tf-subnet"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.vpcTerraform.id
}

resource "aws_eip" "TerraEIP" {
  vpc = true
  instance                  = aws_instance.web.id
  depends_on                = [aws_internet_gateway.gw]
}

resource "aws_route_table" "TerraRouteTB" {
  vpc_id = aws_vpc.vpcTerraform.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
	
  tags = {
    Name = "RouteTable-TF"
  }
}

resource "aws_route_table_association" "routeTB-associat" {
  subnet_id      = aws_subnet.TerraformSubnet.id
  route_table_id = aws_route_table.TerraRouteTB.id
}

resource "aws_security_group" "forwarder" {

  vpc_id = aws_vpc.vpcTerraform.id
  tags = {
         Name = "sg_TF"
       }
  ingress {
    from_port = 0
    protocol = "tcp"
    to_port = 65535
    cidr_blocks = ["0.0.0.0/0"] 
    ipv6_cidr_blocks = ["::/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "cidr" {
  value       = aws_vpc.vpcTerraform
  description = "This is cidr ip range"
}

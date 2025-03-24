# Amazon Linux Management Examples

This document provides examples on how to use the `EC2AL` class from the `pulumi_easy` package to create and manage Amazon Linux instances.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Amazon Linux AMI Lookup](#amazon-linux-ami-lookup)
- [Creating Amazon Linux 2 Instances](#creating-amazon-linux-2-instances)
- [Creating Amazon Linux 2023 Instances](#creating-amazon-linux-2023-instances)
- [Using User Data](#using-user-data)
- [Complete Example](#complete-example)

## Basic Usage

First, import the EC2AL class and initialize it:

```python
import pulumi_easy as easy

# Initialize the EC2AL manager
al_manager = easy.EC2AL()
```

## Amazon Linux AMI Lookup

Look up the latest Amazon Linux AMI by version and architecture:

```python
# Get the latest Amazon Linux 2 x86_64 AMI
al2_x86 = al_manager.get_amazon_linux_ami("2", "x86_64")

# Get the latest Amazon Linux 2023 ARM64 AMI
al2023_arm = al_manager.get_amazon_linux_ami("3", "arm64")

# Use the AMI ID
print(f"Amazon Linux 2 x86_64 AMI ID: {al2_x86.id}")
print(f"Amazon Linux 2023 ARM64 AMI ID: {al2023_arm.id}")
```

## Creating Amazon Linux 2 Instances

Create an Amazon Linux 2 EC2 instance:

```python
# Create an Amazon Linux 2 instance
instance = al_manager.create_amazon_linux_instance(
    name="al2-server",
    storage=20,                  # 20 GB root volume
    version="2",                 # Amazon Linux 2
    arch="x86_64",               # x86_64 architecture
    instance_type="t3.micro",    # Instance type
    ssh_key_name="my-key-pair"   # Key pair name
)

# Access instance properties
print(f"Instance ID: {instance.id}")
print(f"Public IP: {instance.public_ip}")
```

## Creating Amazon Linux 2023 Instances

Amazon Linux 2023 is the latest generation of Amazon Linux:

```python
# Create an Amazon Linux 2023 ARM64 instance (Graviton)
al2023_instance = al_manager.create_amazon_linux_instance(
    name="al2023-server",
    storage=20,                  # 20 GB root volume
    version="3",                 # Amazon Linux 2023
    arch="arm64",                # ARM64 architecture
    instance_type="t4g.nano",    # ARM-based instance type
    ssh_key_name="my-key-pair"   # Key pair name
)
```

## Using User Data

You can provide user data to bootstrap your instance:

```python
# Script to install and start a web server
user_data = """#!/bin/bash
# Update system packages
yum update -y

# Install Apache web server
yum install -y httpd

# Start and enable Apache
systemctl start httpd
systemctl enable httpd

# Create a simple webpage
echo "<h1>Hello from Pulumi Easy!</h1>" > /var/www/html/index.html
"""

# Create an Amazon Linux instance with user data
web_server = al_manager.create_amazon_linux_instance(
    name="web-server",
    storage=20,
    version="2",
    arch="x86_64",
    instance_type="t3.micro",
    ssh_key_name="my-key-pair",
    user_data=user_data
)
```

## Complete Example

Here's a complete example that demonstrates creating an Amazon Linux instance with IP restrictions and tags:

```python
import pulumi
import pulumi_easy as easy

# Get your public IP for secure SSH access
ip_info = easy.get_my_ip()
my_ipv4 = ip_info['ipv4']

# Initialize managers
ec2_manager = easy.EC2Manager()
al_manager = easy.EC2AL()

# Create a key pair
key_pair = ec2_manager.create_key_pair(
    name="al-server-key",
    public_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@hostname"
)

# Create an Amazon Linux 2023 ARM64 instance with restricted SSH access
instance = al_manager.create_amazon_linux_instance(
    name="api-server",
    storage=30,                   # 30 GB root volume
    version="3",                  # Amazon Linux 2023
    arch="arm64",                 # ARM architecture (Graviton)
    instance_type="t4g.small",    # ARM-based instance type
    ssh_key_name=key_pair.key_name,
    my_ipv4=my_ipv4,              # Restrict SSH to your IP
    additional_tags={
        "Environment": "Production",
        "Service": "API",
        "ManagedBy": "Pulumi"
    }
)

# Export the instance's public IP address
pulumi.export("api_server_public_ip", instance.public_ip)
```

This example creates:

1. An SSH key pair using your existing public key
2. A security group allowing SSH access only from your IP address
3. An Amazon Linux 2023 ARM64 EC2 instance with a 30GB root volume
4. Custom tags for better resource management

The instance's public IP address is exported as a stack output.

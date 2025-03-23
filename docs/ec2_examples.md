# EC2 Management Examples

This document provides examples on how to use the `EC2Manager` class from the `pulumi_easy` package.

## Table of Contents

- [Basic Usage](#basic-usage)
- [AMI Lookup](#ami-lookup)
- [Key Pair Creation](#key-pair-creation)
- [Security Group Creation](#security-group-creation)
- [EC2 Instance Creation](#ec2-instance-creation)
- [Complete Example](#complete-example)

## Basic Usage

First, import the EC2Manager class and initialize it:

```python
from pulumi_easy.aws.ec2.ec2 import EC2Manager

# Initialize the EC2Manager
ec2_manager = EC2Manager()
```

## AMI Lookup

Look up the latest Ubuntu AMI by version and architecture:

```python
# Get the latest Ubuntu 22.04 AMD64 AMI
ubuntu_amd64 = ec2_manager.get_ubuntu_ami("22.04", "amd64")

# Get the latest Ubuntu 24.04 ARM64 AMI
ubuntu_arm64 = ec2_manager.get_ubuntu_ami("24.04", "arm64")

# Use the AMI ID
print(f"Ubuntu 22.04 AMD64 AMI ID: {ubuntu_amd64.id}")
print(f"Ubuntu 24.04 ARM64 AMI ID: {ubuntu_arm64.id}")
```

## Key Pair Creation

Create an EC2 key pair using your existing public key:

```python
# Create a key pair using an existing public key
key_pair = ec2_manager.create_key_pair(
    name="my-project-key",
    public_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@hostname"
)

# The key_pair.key_name can be used when creating EC2 instances
```

## Security Group Creation

Create a security group that allows SSH access:

```python
# Create a basic security group with SSH access
security_group = ec2_manager.create_security_group(
    name="web-server-sg",
    description="Security group for web servers"
)
```

## EC2 Instance Creation

Create an Ubuntu EC2 instance:

```python
# Create an Ubuntu 22.04 instance
instance = ec2_manager.create_ubuntu_instance(
    name="web-server",
    storage=20,                  # 20 GB root volume
    version="22.04",             # Ubuntu version
    arch="amd64",                # Architecture
    instance_type="t2.micro",    # Instance type
    ssh_key_name="my-project-key"  # Key pair name
)

# Access instance properties
print(f"Instance ID: {instance.id}")
print(f"Public IP: {instance.public_ip}")
```

## Complete Example

Here's a complete example that demonstrates creating an EC2 instance with all the necessary resources:

```python
import pulumi
from pulumi_easy.aws.ec2.ec2 import EC2Manager

# Initialize the EC2Manager
ec2_manager = EC2Manager()

# Create a key pair
key_pair = ec2_manager.create_key_pair(
    name="my-project-key",
    public_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@hostname"
)

# Create an Ubuntu instance with all necessary components
instance = ec2_manager.create_ubuntu_instance(
    name="api-server",
    storage=30,                   # 30 GB root volume
    version="24.04",              # Ubuntu version
    arch="arm64",                 # ARM architecture (graviton)
    instance_type="t4g.small",    # ARM-based instance type
    ssh_key_name=key_pair.key_name
)

# Export the instance's public IP address
pulumi.export("instance_public_ip", instance.public_ip)
```

This example creates:

1. An SSH key pair using your existing public key
2. A security group allowing SSH access (created by `create_ubuntu_instance`)
3. An Ubuntu 24.04 ARM64 EC2 instance with a 30GB root volume

The instance's public IP address is exported as a stack output.

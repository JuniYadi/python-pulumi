# Import Patterns for Pulumi Easy

This document demonstrates the different ways to import and use the `pulumi_easy` package.

## Traditional Import Style

You can import specific classes and functions directly from their modules:

```python
# Import EC2Manager directly from its module
from pulumi_easy.aws.ec2.ec2 import EC2Manager

# Import IAM managers from their modules
from pulumi_easy.aws.iam.iam import IamManager
from pulumi_easy.aws.iam.s3 import IamRoleS3Manager

# Import utility functions
from pulumi_easy.utils.ip import get_my_ip

# Usage
ec2_manager = EC2Manager()
iam_manager = IamManager()
```

## Simplified Import Style

With the new structure, you can use a more concise import style:

```python
# Import everything at once
import pulumi_easy as easy

# Access classes and functions
ec2_manager = easy.EC2Manager()
iam_manager = easy.IamManager()
my_ip = easy.get_my_ip()
```

## Module-Level Imports

You can also import just the modules you need:

```python
# Import the AWS module
from pulumi_easy import aws

# Use EC2 and IAM managers
ec2_manager = aws.ec2.EC2Manager()
iam_manager = aws.iam.IamManager()
```

## Individual Class Imports

Direct imports of the most commonly used classes are still supported:

```python
# Import just what you need
from pulumi_easy import EC2Manager, get_my_ip

# Use the imported classes and functions
ec2_manager = EC2Manager()
ip_info = get_my_ip()
```

## Complete Example

Here's a complete example using the simplified import style:

```python
import pulumi
import pulumi_easy as easy

# Get our public IP address
ip_info = easy.get_my_ip()
my_ipv4 = ip_info['ipv4']

# Create a key pair
ec2 = easy.EC2Manager()
key_pair = ec2.create_key_pair(
    name="my-key",
    public_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@hostname"
)

# Create a security group that allows SSH only from our IP
security_group = ec2.create_security_group(
    name="secure-sg",
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": [f"{my_ipv4}/32"],
            "description": "SSH access from my IP only",
        },
    ]
)

# Create an Ubuntu instance
instance = ec2.create_ubuntu_instance(
    name="web-server",
    storage=20,
    version="22.04",
    arch="arm64",
    instance_type="t4g.nano",
    ssh_key_name=key_pair.key_name,
    security_group=security_group
)

# Create IAM role for S3 access
iam = easy.IamRoleS3Manager()
role = iam.create_iam_ec2_s3(
    name="web-s3-access",
    bucket_resources=[
        "arn:aws:s3:::my-data-bucket/*",
        "arn:aws:s3:::my-data-bucket"
    ]
)

# Export the instance's public IP
pulumi.export("instance_public_ip", instance.public_ip)
```

# Pulumi Easy

A streamlined Python library for AWS infrastructure provisioning using Pulumi.

## Overview

`pulumi-easy` is a Python package that simplifies AWS infrastructure-as-code using Pulumi. It provides higher-level abstractions that make it easier to create common AWS resources without having to write boilerplate code.

## Installation

```bash
# Using pip
pip install pulumi-easy

# Using poetry
poetry add pulumi-easy

# Using uv
uv add pulumi-easy
```

## Requirements

- Python 3.12+
- Pulumi CLI
- AWS credentials configured

## Getting Started

1. Install Pulumi CLI by following the [official guide](https://www.pulumi.com/docs/get-started/install/)

```bash
# MacOS
brew install pulumi/tap/pulumi

# Linux
curl -fsSL https://get.pulumi.com | sh

# Windows
# Please refer to the official guide
```

2. Configure AWS credentials using the `aws configure` command

```bash
aws configure
```

3. Initialize a new Pulumi project

```bash
pulumi new aws-python
```

4. Install the `pulumi-easy` package

```bash
pip install pulumi-easy
```

5. Start using the library in your Pulumi program

```python
from pulumi_easy.aws.iam.s3 import IamRoleS3Manager

# Initialize the manager
iam_manager = IamRoleS3Manager()

# Create an IAM role for EC2 to access specific S3 buckets
role = iam_manager.create_iam_ec2_s3(
    name="my-ec2-s3-role",
    bucket_resources=[
        "arn:aws:s3:::my-bucket/*",
        "arn:aws:s3:::my-bucket"
    ]
)
```

### Optional Dependencies

By default, the library does not include any dependencies. However, you can install additional packages to enable more features:

| Package | Description |
|---------|-------------|
| `requests` | Required for `get_my_ip()` function in `pulumi_easy.utils.ip` |

## Benefits

- **Simplified Syntax**: Create AWS resources with less code and cleaner APIs
- **Best Practices Built-in**: IAM policies, security groups, and other resources follow AWS best practices
- **Type Safety**: Python type hints for better IDE integration and error detection
- **Modular Design**: Use only what you need from the library
- **Production-Ready**: Designed to be used in real-world projects

## Usage Examples

### Create an IAM Role for EC2 to Access S3

```python
from pulumi_easy.aws.iam.s3 import IamRoleS3Manager

# Initialize the manager
iam_manager = IamRoleS3Manager()

# Create an IAM role for EC2 to access specific S3 buckets
role = iam_manager.create_iam_ec2_s3(
    name="my-ec2-s3-role",
    bucket_resources=[
        "arn:aws:s3:::my-bucket/*",
        "arn:aws:s3:::my-bucket"
    ]
)
```

### Create an Ubuntu EC2 Instance

```python
from pulumi_easy.aws.ec2.ec2 import EC2Manager

# Initialize the manager
ec2_manager = EC2Manager()

# Create a key pair
key_pair = ec2_manager.create_key_pair(
    name="my-key",
    public_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@hostname"
)

# Create an Ubuntu instance
instance = ec2_manager.create_ubuntu_instance(
    name="web-server",
    storage=20,                  # 20 GB root volume
    version="22.04",             # Ubuntu version
    arch="arm64",                # Architecture
    instance_type="t4g.nano",    # Instance type
    ssh_key_name=key_pair.key_name
)
```

See more examples in the [documentation](docs).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

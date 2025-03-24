"""
Pulumi Easy - Simplified AWS infrastructure provisioning with Pulumi

This package provides higher-level abstractions for AWS infrastructure-as-code
using Pulumi, making it easier to create common AWS resources.
"""

# Import and re-export submodules
from . import aws
from . import utils

# Import and re-export commonly used classes for convenience
from .aws.ec2.ec2 import EC2Manager
from .aws.iam.iam import IamManager
from .aws.iam.s3 import IamRoleS3Manager
from .utils.ip import get_my_ip

__version__ = "0.4.0"

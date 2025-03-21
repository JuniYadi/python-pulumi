import pulumi_aws as aws
from .iam import IamManager

class IamRoleS3Manager(IamManager):  
    """
    A manager class for creating IAM roles and policies specifically for granting 
    EC2 instances access to S3 buckets. Inherits from the IamManager base class.
    """
    
    def create_iam_ec2_s3(self,
                            name,
                            bucket_resources,
                            bucket_permissions=None,
                            description=None,
                            services=["ec2.amazonaws.com"]):
        """
        Creates an IAM role and policy for EC2 instances to access S3 buckets.

        Args:
            name (str): Name of the IAM role and policy.
            bucket_resources (list): List of S3 bucket ARNs to grant access to.
            bucket_permissions (list, optional): List of S3 permissions to grant. 
                Defaults to common read/write/delete permissions.
            description (str, optional): Description for the policy. Defaults to 
                a generated description based on the role name.
            services (list, optional): List of AWS services allowed to assume the role. 
                Defaults to ["ec2.amazonaws.com"].

        Returns:
            dict: A dictionary containing ARNs and names of the created IAM role and policy.
        """
        # Set default description if none is provided
        if description is None:
            description = f"Policy allowing EC2 access to S3 buckets ({name})"
        
        # Set default bucket permissions if none are provided
        if bucket_permissions is None:
            bucket_permissions = [
                "s3:GetObject",
                "s3:GetObjectAcl",
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:DeleteObject",
            ]
        
        # Define the policy document for S3 access
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": ["s3:ListBucket"],
                    "Effect": "Allow",
                    "Resource": "*",
                },
                {
                    "Action": bucket_permissions,
                    "Effect": "Allow",
                    "Resource": bucket_resources,
                },
            ],
        }
        
        # Call the base class method to create the IAM role and attach the policy
        return self.create_iam_role_with_policy(
            name=name,
            assume_role_services=services,
            policy_document=policy_document,
            description=description
        )
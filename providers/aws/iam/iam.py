import pulumi
import pulumi_aws as aws
import json

class IamManager:
    """
    Class for managing AWS IAM roles and policies with Pulumi.
    Provides methods to create different types of IAM roles with specific permissions
    and dynamic trust relationships.
    """
    
    def __init__(self):
        """
        Initializes the IamManager class.
        """
        pass
    
    def get_assume_role_policy(self, service_identifiers):
        """
        Creates an assume role policy document for specified AWS services.
        
        Args:
            service_identifiers (list): List of AWS service identifiers 
                (e.g., ["ec2.amazonaws.com", "lambda.amazonaws.com"]).
            
        Returns:
            aws.iam.GetPolicyDocumentResult: IAM policy document for assuming roles.
        """
        return aws.iam.get_policy_document(statements=[{
            "actions": ["sts:AssumeRole"],
            "principals": [{
                "type": "Service",
                "identifiers": service_identifiers,
            }],
        }])

    def create_iam_role_with_policy(self, 
                                    name, assume_role_services, policy_document, description=None):
        """
        Creates an IAM role with the specified policy and assume role configuration.
        
        Args:
            name (str): Name of the IAM role and policy.
            assume_role_services (list): List of services that can assume this role 
                (e.g., ["ec2.amazonaws.com"]).
            policy_document (dict): Dictionary containing the IAM policy document.
            description (str, optional): Optional description for the policy. Defaults to None.
            
        Returns:
            dict: Dictionary containing ARNs and names of created resources.
        """
        if description is None:
            description = f"Policy for {name}"
            
        assume_role_policy = self.get_assume_role_policy(assume_role_services)
        
        policy = aws.iam.Policy(f"policy_{name}",
            name=name,
            path="/",
            description=description,
            policy=json.dumps(policy_document))
        
        role = aws.iam.Role(f"role_{name}",
            name=name,
            assume_role_policy=assume_role_policy.json,
            managed_policy_arns=[policy.arn])
        
        # Only create instance profile if EC2 is one of the services
        profile = None
        if "ec2.amazonaws.com" in assume_role_services:
            profile = aws.iam.InstanceProfile(f"profile_{name}",
                name=name,
                role=role.name)
        
        # Export resources
        pulumi.export(f"policy_arn_{name}", policy.arn)
        pulumi.export(f"role_arn_{name}", role.arn)
        
        result = {
            "policy_arn": policy.arn,
            "role_arn": role.arn,
        }
        
        if profile:
            pulumi.export(f"instance_profile_{name}", profile.name)
            result["profile_name"] = profile.name
            
        return result
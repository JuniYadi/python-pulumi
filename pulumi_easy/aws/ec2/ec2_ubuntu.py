import pulumi
from .ec2 import EC2Manager

class EC2Ubuntu(EC2Manager):
    """
    Class for managing AWS EC2 Ubuntu instances with Pulumi.
    Extends EC2Manager with Ubuntu-specific instance creation capabilities.
    """
    
    def create_ubuntu_instance(self, name: str, storage: int, version: str, 
                        arch: str, instance_type: str, ssh_key_name: str,
                        security_group=None, iam_instance_profile=None,
                        my_ipv4=None, my_ipv6=None, additional_tags=None, user_data=None):
        """
        Creates an Ubuntu EC2 instance with specified parameters.
        
        Args:
            name (str): Name for the EC2 instance
            storage (int): Root EBS volume size in GB
            version (str): Ubuntu version (e.g., "22.04")
            arch (str): Architecture (e.g., "amd64", "arm64")
            instance_type (str): EC2 instance type (e.g., "t2.micro", "t4g.nano")
            ssh_key_name (str): Name of the SSH key pair to use
            security_group (aws.ec2.SecurityGroup, optional): Custom security group. 
                If not provided, a default one will be created.
            iam_instance_profile (str, optional): The IAM instance profile to associate 
                with the instance.
            my_ipv4 (str, optional): Your IPv4 address for restricted SSH access (e.g., "203.0.113.1/32")
            my_ipv6 (str, optional): Your IPv6 address for restricted SSH access (e.g., "2001:DB8::1/128")
            additional_tags (dict, optional): Additional tags to apply to the instance
            user_data (str, optional): User data script to run at launch time
            
        Returns:
            aws.ec2.Instance: The created EC2 instance resource
            
        Example:
            ```python
            ec2_ubuntu = EC2Ubuntu()
            # With IP restrictions
            instance1 = ec2_ubuntu.create_ubuntu_instance(
                name="web-server",
                storage=20,
                version="22.04",
                arch="amd64",
                instance_type="t2.micro",
                ssh_key_name="my-key-pair",
                my_ipv4="203.0.113.1/32"
            )
            ```
        """
        ami = self.get_ubuntu_ami(version, arch)
        
        # Check for architecture compatibility
        is_arm_instance = any(arm_prefix in instance_type for arm_prefix in ["a1.", "t4g.", "c6g.", "c7g.", "m6g.", "r6g.", "x2gd."])
        is_arm_ami = "arm64" in arch
        
        if is_arm_instance and not is_arm_ami:
            pulumi.log.warn(f"WARNING: You are using an ARM-based instance type ({instance_type}) with a non-ARM AMI. This may fail.")
        elif not is_arm_instance and is_arm_ami:
            pulumi.log.warn(f"WARNING: You are using an x86 instance type ({instance_type}) with an ARM AMI. This will likely fail.")
        
        # Set default additional tags with OS info
        os_tags = {
            "OS": "Ubuntu",
            "Version": version,
            "Architecture": arch
        }
        
        # Merge with provided additional tags if they exist
        if additional_tags:
            os_tags.update(additional_tags)
        
        # Root device for Ubuntu is typically /dev/sda1, but may vary
        root_device = "/dev/sda1"
            
        return self.create_instance(
            name=name,
            ami_id=ami.id,
            storage=storage,
            instance_type=instance_type,
            ssh_key_name=ssh_key_name,
            security_group=security_group,
            iam_instance_profile=iam_instance_profile,
            my_ipv4=my_ipv4,
            my_ipv6=my_ipv6,
            additional_tags=os_tags,
            user_data=user_data,
            root_device_name=root_device
        )

import pulumi
import pulumi_aws as aws

class EC2Manager:
    """
    Class for managing AWS EC2 resources with Pulumi.
    Provides methods to create EC2 instances, security groups, key pairs, and AMI lookups.
    """
    
    def __init__(self):
        """
        Initializes the EC2Manager class.
        """
        pass
    
    def get_ubuntu_ami(self, version: str, arch: str):
        """
        Gets the latest Ubuntu AMI ID for a specified version and architecture.
        
        Args:
            version (str): Ubuntu version (e.g., "20.04", "22.04", "24.04")
            arch (str): Architecture (e.g., "amd64", "arm64")
            
        Returns:
            aws.ec2.GetAmiResult: Resulting AMI lookup with id, arn, name and other properties
            
        Example:
            ```python
            ec2_manager = EC2Manager()
            ami = ec2_manager.get_ubuntu_ami("22.04", "amd64")
            ```
        """
        # Get ubuntu name based on version
        if version == "20.04":
            ubuntu_name = "hvm-ssd/ubuntu-focal-20.04"
        elif version == "22.04":
            ubuntu_name = "hvm-ssd/ubuntu-jammy-22.04"
        elif version == "24.04":
            ubuntu_name = "hvm-ssd-gp3/ubuntu-noble-24.04"
        else:
            ubuntu_name = f"*-{version}"

        # Dynamic Array Filter
        filters = [
            {
                "name": "name",
                "values": [f"ubuntu/images/{ubuntu_name}-{arch}-server-*"],
            },
            {
                "name": "virtualization-type",
                "values": ["hvm"],
            },
        ]

        # Get the latest Ubuntu AMI
        ubuntu = aws.ec2.get_ami(most_recent=True,
                                filters=filters,
                                owners=["099720109477"])

        # Default Pulumi Export
        pulumi.export(f"ubuntu_id_{version}_{arch}", ubuntu.id)
        pulumi.export(f"ubuntu_arn_{version}_{arch}", ubuntu.arn)
        pulumi.export(f"ubuntu_name_{version}_{arch}", ubuntu.name)

        return ubuntu
    
    def get_amazon_linux_ami(self, version: str, arch: str):
        """
        Gets the latest Amazon Linux AMI ID for a specified version and architecture.
        
        Args:
            version (str): Amazon Linux version (e.g., "2" or "3")
            arch (str): Architecture (e.g., "x86_64", "arm64")
            
        Returns:
            aws.ec2.GetAmiResult: Resulting AMI lookup with id, arn, name and other properties
            
        Example:
            ```python
            ec2_manager = EC2Manager()
            ami = ec2_manager.get_amazon_linux_ami("2", "x86_64")
            ```
        """
        # Get amazon name based on version
        if version == "2":
            amazon_name = f"amzn2-ami-*-{arch}-gp2"
        else:
            amazon_name = f"al2023-ami-2023.*-{arch}"

        # Dynamic Array Filter
        filters = [
            {
                "name": "name",
                "values": [amazon_name],
            },
            {
                "name": "virtualization-type",
                "values": ["hvm"],
            },
        ]

        # Get the latest Amazon Linux AMI
        amazon = aws.ec2.get_ami(most_recent=True,
                                filters=filters,
                                owners=["amazon"])

        # Default Pulumi Export
        pulumi.export(f"amazon_id_{version}_{arch}", amazon.id)
        pulumi.export(f"amazon_arn_{version}_{arch}", amazon.arn)
        pulumi.export(f"amazon_name_{version}_{arch}", amazon.name)

        return amazon
    
    def create_key_pair(self, name: str, public_key: str):
        """
        Creates an EC2 key pair using a provided public key.
        
        Args:
            name (str): Name for the key pair
            public_key (str): Public key material (e.g., the contents of an id_rsa.pub file)
            
        Returns:
            aws.ec2.KeyPair: The created EC2 key pair resource
            
        Example:
            ```python
            ec2_manager = EC2Manager()
            key_pair = ec2_manager.create_key_pair(
                name="my-key-pair",
                public_key="ssh-rsa AAAAB3NzaC1yc2E..."
            )
            ```
        """
        key = aws.ec2.KeyPair(f"create_key_pair_{name}",
                            key_name=name,
                            public_key=public_key)

        pulumi.export("key_name", key.key_name)

        return key

    def create_security_group(self, name: str, description: str = "Security group for SSH access",
                              ingress=None, egress=None):
        """
        Create a security group that allows SSH access on port 22.
        
        Args:
            name (str): Name for the security group
            description (str, optional): Description for the security group. 
                Defaults to "Security group for SSH access".
                
        Returns:
            aws.ec2.SecurityGroup: The created security group resource
            
        Example:
            ```python
            ec2_manager = EC2Manager()
            sg = ec2_manager.create_security_group("web-server-sg", "Web server security group")
            ```
        """
        
        if ingress is None:
            ingress = [
                        {
                            "protocol": "tcp",
                            "from_port": 22,
                            "to_port": 22,
                            "cidr_blocks": ["0.0.0.0/0"],
                            "description": "SSH access from anywhere",
                        },
                    ]
            
        if egress is None:
            egress = [
                        {
                            "protocol": "-1",  # All protocols
                            "from_port": 0,
                            "to_port": 0,
                            "cidr_blocks": ["0.0.0.0/0"],
                            "description": "Allow all outbound traffic",
                        },
                    ]
        
        
        sg = aws.ec2.SecurityGroup(f"security_group_{name}",
                                name=name,
                                description=description,
                                ingress=ingress,
                                egress=egress,
                                tags={
                                    "Name": name,
                                })

        pulumi.export(f"security_group_{name}_id", sg.id)
        pulumi.export(f"security_group_{name}_name", sg.name)

        return sg

    def create_instance(self, name: str, ami_id: str, storage: int, instance_type: str, ssh_key_name: str,
                    security_group=None, iam_instance_profile=None, my_ipv4=None, my_ipv6=None, 
                    additional_tags=None, user_data=None, volume_type="gp3", root_device_name="/dev/sda1",
                    subnet_id=None, vpc_id=None):
        """
        Creates a generic EC2 instance with specified parameters.
        
        Args:
            name (str): Name for the EC2 instance
            ami_id (str): AMI ID for the instance
            storage (int): Root EBS volume size in GB
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
            volume_type (str, optional): EBS volume type, defaults to "gp3"
            root_device_name (str, optional): Root device name, defaults to "/dev/sda1" 
                but may be different for some AMIs
            subnet_id (str, optional): ID of the subnet to launch the instance in.
                If provided, the instance will be launched in a VPC
            vpc_id (str, optional): ID of the VPC where security group should be created.
                Required when subnet_id is provided and security_group is not
            
        Returns:
            aws.ec2.Instance: The created EC2 instance resource
        """
        # Check if we're working with a VPC
        is_vpc = subnet_id is not None
        
        # Create a security group with IP restrictions if my_ipv4 or my_ipv6 are provided
        if my_ipv4 or my_ipv6:
            ingress_rules = []
            
            # Add SSH rule for IPv4 if provided
            if my_ipv4:
                ipv4_cidr = my_ipv4 if "/" in my_ipv4 else f"{my_ipv4}/32"
                ingress_rules.append({
                    "protocol": "tcp",
                    "from_port": 22,
                    "to_port": 22,
                    "cidr_blocks": [ipv4_cidr],
                    "description": "SSH access from my IPv4 address",
                })
                pulumi.export("ec2_ssh_ipv4", ipv4_cidr)
            
            # Add SSH rule for IPv6 if provided
            if my_ipv6:
                ipv6_cidr = my_ipv6 if "/" in my_ipv6 else f"{my_ipv6}/128"
                ingress_rules.append({
                    "protocol": "tcp",
                    "from_port": 22,
                    "to_port": 22,
                    "ipv6_cidr_blocks": [ipv6_cidr],
                    "description": "SSH access from my IPv6 address",
                })
                pulumi.export("ec2_ssh_ipv6", ipv6_cidr)
            
            # If we're in a VPC, we need to create a VPC security group
            if is_vpc:
                if vpc_id is None:
                    pulumi.log.warn("vpc_id is required when creating a security group for an instance in a VPC. Attempting to extract VPC ID from subnet.")
                    # Try to get VPC ID from the subnet
                    try:
                        subnet_info = aws.ec2.get_subnet(id=subnet_id)
                        vpc_id = subnet_info.vpc_id
                    except Exception as e:
                        pulumi.log.error(f"Could not determine VPC ID from subnet: {str(e)}")
                        raise ValueError("vpc_id is required when creating a security group for an instance in a VPC")
                
                # Create a VPC security group
                sg_name = f"{name}-vpc-restricted"
                security_group = aws.ec2.SecurityGroup(
                    f"security_group_{sg_name}",
                    name=sg_name,
                    description=f"Security group with restricted SSH access for {name}",
                    vpc_id=vpc_id,
                    ingress=ingress_rules,
                    egress=[{
                        "protocol": "-1",  # All protocols
                        "from_port": 0,
                        "to_port": 0,
                        "cidr_blocks": ["0.0.0.0/0"],
                        "description": "Allow all outbound traffic",
                    }],
                    tags={"Name": sg_name}
                )
            else:
                # Create a classic security group
                security_group = self.create_security_group(
                    f"{name}-restricted",
                    description=f"Security group with restricted SSH access for {name}",
                    ingress=ingress_rules
                )
        # Use provided security group or create a default one
        elif security_group is None:
            if is_vpc:
                if vpc_id is None:
                    pulumi.log.warn("vpc_id is required when creating a security group for an instance in a VPC. Attempting to extract VPC ID from subnet.")
                    # Try to get VPC ID from the subnet
                    try:
                        subnet_info = aws.ec2.get_subnet(id=subnet_id)
                        vpc_id = subnet_info.vpc_id
                    except Exception as e:
                        pulumi.log.error(f"Could not determine VPC ID from subnet: {str(e)}")
                        raise ValueError("vpc_id is required when creating a security group for an instance in a VPC")
                
                # Create a VPC security group
                sg_name = f"{name}-vpc"
                security_group = aws.ec2.SecurityGroup(
                    f"security_group_{sg_name}",
                    name=sg_name,
                    description=f"Security group for {name}",
                    vpc_id=vpc_id,
                    ingress=[{
                        "protocol": "tcp",
                        "from_port": 22,
                        "to_port": 22,
                        "cidr_blocks": ["0.0.0.0/0"],
                        "description": "SSH access from anywhere",
                    }],
                    egress=[{
                        "protocol": "-1",  # All protocols
                        "from_port": 0,
                        "to_port": 0,
                        "cidr_blocks": ["0.0.0.0/0"],
                        "description": "Allow all outbound traffic",
                    }],
                    tags={"Name": sg_name}
                )
            else:
                # Create a classic security group
                security_group = self.create_security_group(name)
        
        # Set up base tags
        tags = {"Name": name}
        
        # Add additional tags if provided
        if additional_tags:
            tags.update(additional_tags)
            
        # Log instance details for debugging
        pulumi.log.info(f"Creating instance '{name}' with AMI ID: {ami_id}, type: {instance_type}")
        
        # Get AMI details to determine root device name
        try:
            ami_info = aws.ec2.get_ami(ami_ids=[ami_id], owners=["amazon", "099720109477", "self"])
            if ami_info and ami_info.root_device_name:
                root_device_name = ami_info.root_device_name
                pulumi.log.info(f"Using root device name '{root_device_name}' from AMI")
        except Exception as e:
            pulumi.log.warn(f"Could not fetch AMI details, using default root device name '{root_device_name}': {str(e)}")
        
        # Configure instance arguments differently based on whether we're using a VPC
        instance_args = {
            "instance_type": instance_type,
            "ami": ami_id,
            "root_block_device": {
                "volume_size": storage,
                "volume_type": volume_type,
                "delete_on_termination": True,
            },
            "key_name": ssh_key_name,
            "tags": tags
        }
        
        # Subnet ID is provided for VPC instances
        if is_vpc:
            instance_args["subnet_id"] = subnet_id
            instance_args["vpc_security_group_ids"] = [security_group.id]
        else:
            instance_args["security_groups"] = [security_group.name]
        
        # Add IAM instance profile if provided
        if iam_instance_profile:
            instance_args["iam_instance_profile"] = iam_instance_profile
            
        # Add user data if provided
        if user_data:
            instance_args["user_data"] = user_data
        
        instance = aws.ec2.Instance(name, **instance_args)

        pulumi.export(f"ec2_{name}_id", instance.id)
        pulumi.export(f"ec2_{name}_public_ip", instance.public_ip)
        
        return instance

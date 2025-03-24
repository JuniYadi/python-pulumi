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

    def create_ubuntu_instance(self, name: str, storage: int, version: str, 
                            arch: str, instance_type: str, ssh_key_name: str,
                            security_group=None, iam_instance_profile=None,
                            my_ipv4=None, my_ipv6=None):
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
            
        Returns:
            aws.ec2.Instance: The created EC2 instance resource
            
        Example:
            ```python
            ec2_manager = EC2Manager()
            # With IP restrictions
            instance1 = ec2_manager.create_ubuntu_instance(
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
        
        # Create a security group with IP restrictions if my_ipv4 or my_ipv6 are provided
        if my_ipv4 or my_ipv6:
            ingress_rules = []
            
            # Add SSH rule for IPv4 if provided
            if my_ipv4:
                ipv4_cidr = f"{my_ipv4}/32"
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
                ipv6_cidr = f"{my_ipv6}/128"
                ingress_rules.append({
                    "protocol": "tcp",
                    "from_port": 22,
                    "to_port": 22,
                    "ipv6_cidr_blocks": [f"{ipv6_cidr}"],
                    "description": "SSH access from my IPv6 address",
                })
                pulumi.export("ec2_ssh_ipv6", ipv6_cidr)
            
            security_group = self.create_security_group(
                f"{name}-restricted",
                description=f"Security group with restricted SSH access for {name}",
                ingress=ingress_rules
            )
        # Use provided security group or create a default one
        elif security_group is None:
            security_group = self.create_security_group(name)
        
        instance_args = {
            "instance_type": instance_type,
            "ami": ami.id,
            "ebs_block_devices": [{
                "device_name": "/dev/sda1",
                "volume_size": storage,
                "volume_type": "gp3",
            }],
            "key_name": ssh_key_name,
            "security_groups": [security_group.name],
            "tags": {
                "Name": name,
            }
        }
        
        # Add IAM instance profile if provided
        if iam_instance_profile:
            instance_args["iam_instance_profile"] = iam_instance_profile
        
        instance = aws.ec2.Instance(name, **instance_args)

        pulumi.export(f"ec2_{name}_id", instance.id)
        pulumi.export(f"ec2_{name}_public_ip", instance.public_ip)
        
        return instance

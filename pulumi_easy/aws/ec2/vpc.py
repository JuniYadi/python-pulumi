import pulumi
import pulumi_aws as aws
import ipaddress

class EC2VPC:
    def __init__(self, name: str, cidr_block: str = "10.0.0.0/16", public_subnet_cidrs=None, private_subnet_cidrs=None):
        self.name = name
        self.cidr_block = cidr_block
        self.vpc = None
        self.public_subnets = []
        self.private_subnets = []
        self.internet_gateway = None
        self.public_route_table = None
        self.private_route_table = None
        
        # Generate subnet CIDRs if not provided
        if public_subnet_cidrs is None and private_subnet_cidrs is None:
            generated_cidrs = self._generate_subnet_cidrs(self.cidr_block)
            self.public_subnet_cidrs = generated_cidrs['public']
            self.private_subnet_cidrs = generated_cidrs['private']
        else:
            self.public_subnet_cidrs = public_subnet_cidrs or []
            self.private_subnet_cidrs = private_subnet_cidrs or []

    def _generate_subnet_cidrs(self, vpc_cidr, subnet_bits=24):
        """
        Generate subnet CIDRs from VPC CIDR.
        Returns 3 public and 3 private subnets by default.
        """
        try:
            network = ipaddress.ip_network(vpc_cidr)
            subnets = list(network.subnets(new_prefix=subnet_bits))
            
            # Generate at least 6 subnets (3 public + 3 private)
            result = {
                'public': [str(subnets[i]) for i in range(min(3, len(subnets)))],
                'private': [str(subnets[i+3]) for i in range(min(3, len(subnets)-3))]
            }
            return result
        except (ValueError, IndexError):
            # Fallback to hardcoded values if calculation fails
            return {
                'public': ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"],
                'private': ["10.0.3.0/24", "10.0.4.0/24", "10.0.5.0/24"]
            }

    def create(self):
        # Create VPC
        self.vpc = aws.ec2.Vpc(
            f"vpc_{self.name}",
            cidr_block=self.cidr_block,
            enable_dns_support=True,
            enable_dns_hostnames=True,
            assign_generated_ipv6_cidr_block=True,
            tags={
                "Name": self.name,
            }
        )

        # Get available AZs in the region
        available_azs = aws.get_availability_zones(state="available")

        # Create Internet Gateway
        self.create_internet_gateway()
        
        # Create public subnets
        self.create_public_subnets(available_azs.names)
        
        # Create private subnets
        self.create_private_subnets(available_azs.names)
        
        return self.vpc

    def create_internet_gateway(self):
        self.internet_gateway = aws.ec2.InternetGateway(
            f"igw_{self.name}",
            vpc_id=self.vpc.id,
            tags={
                "Name": f"{self.name}-igw"
            }
        )
        
        # Create public route table with separate IPv4 and IPv6 routes
        self.public_route_table = aws.ec2.RouteTable(
            f"rt_public_{self.name}",
            vpc_id=self.vpc.id,
            routes=[
                aws.ec2.RouteTableRouteArgs(
                    cidr_block="0.0.0.0/0",
                    gateway_id=self.internet_gateway.id,
                )
                # IPv6 route will be added separately
            ],
            tags={
                "Name": f"{self.name}-public-rt"
            }
        )
        
        # Create an IPv6 route if the VPC has an IPv6 CIDR block
        # This is created as a separate resource to avoid validation issues with mixed IPv4/IPv6
        aws.ec2.Route(
            f"ipv6_public_route_{self.name}",
            route_table_id=self.public_route_table.id,
            destination_ipv6_cidr_block="::/0",
            gateway_id=self.internet_gateway.id
        )
        
        # Create private route table
        self.private_route_table = aws.ec2.RouteTable(
            f"rt_private_{self.name}",
            vpc_id=self.vpc.id,
            tags={
                "Name": f"{self.name}-private-rt"
            }
        )

    def create_public_subnets(self, az_names):
        # Create public subnets in at least 3 AZs (if available)
        max_azs = min(len(az_names), max(3, len(self.public_subnet_cidrs)))
        
        for i in range(min(max_azs, len(self.public_subnet_cidrs))):
            # Calculate the IPv6 subnet CIDR using the VPC's IPv6 CIDR block
            # The subnet gets a /64 slice from the VPC's /56 by convention
            ipv6_cidr_block = pulumi.Output.all(self.vpc.ipv6_cidr_block).apply(
                lambda args: f"{args[0].split(':')[0:3]}:{i:x}::/64" if args[0] else None
            )
            
            subnet_args = {
                "vpc_id": self.vpc.id,
                "cidr_block": self.public_subnet_cidrs[i],
                "availability_zone": az_names[i],
                "map_public_ip_on_launch": True,
                "enable_resource_name_dns_a_record_on_launch": True,
                "tags": {
                    "Name": f"{self.name}-public-{i+1}"
                }
            }
            
            # Only add IPv6 configuration if we have a valid IPv6 CIDR block
            ipv6_cidr_block.apply(
                lambda cidr: subnet_args.update({
                    "ipv6_cidr_block": cidr,
                    "assign_ipv6_address_on_creation": True if cidr else False,
                    "enable_resource_name_dns_aaaa_record_on_launch": True if cidr else False,
                    "enable_dns64": True if cidr else False,
                }) if cidr else None
            )
            
            subnet = aws.ec2.Subnet(
                f"subnet_public_{self.name}_{i+1}",
                **subnet_args
            )
            self.public_subnets.append(subnet)
            
            # Associate public subnet with the public route table
            aws.ec2.RouteTableAssociation(
                f"rta_public_{self.name}_{i+1}",
                subnet_id=subnet.id,
                route_table_id=self.public_route_table.id
            )

    def create_private_subnets(self, az_names):
        # Create private subnets in at least 3 AZs (if available)
        max_azs = min(len(az_names), max(3, len(self.private_subnet_cidrs)))
        
        for i in range(min(max_azs, len(self.private_subnet_cidrs))):
            subnet = aws.ec2.Subnet(
                f"subnet_private_{self.name}_{i+1}",
                vpc_id=self.vpc.id,
                cidr_block=self.private_subnet_cidrs[i],
                availability_zone=az_names[i],
                tags={
                    "Name": f"{self.name}-private-{i+1}"
                }
            )
            self.private_subnets.append(subnet)
            
            # Associate private subnet with the private route table
            aws.ec2.RouteTableAssociation(
                f"rta_private_{self.name}_{i+1}",
                subnet_id=subnet.id,
                route_table_id=self.private_route_table.id
            )
    
    def export_outputs(self):
        """Export VPC and subnet information as Pulumi stack outputs."""
        pulumi.export(f'vpc_{self.name}_id', self.vpc.id)
        
        # Export public subnet IDs
        public_subnet_ids = [subnet.id for subnet in self.public_subnets]
        pulumi.export(f'vpc_{self.name}_public_subnet_ids', public_subnet_ids)
        
        # Export private subnet IDs
        private_subnet_ids = [subnet.id for subnet in self.private_subnets]
        pulumi.export(f'vpc_{self.name}_private_subnet_ids', private_subnet_ids)
        
        # Export all subnet IDs combined
        all_subnet_ids = public_subnet_ids + private_subnet_ids
        pulumi.export(f'vpc_{self.name}_all_subnet_ids', all_subnet_ids)
        
        return {
            'vpc_id': self.vpc.id,
            'public_subnet_ids': public_subnet_ids,
            'private_subnet_ids': private_subnet_ids,
            'all_subnet_ids': all_subnet_ids
        }
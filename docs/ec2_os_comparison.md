# EC2 Operating System Comparison Guide

This document provides a comparison between using Ubuntu and Amazon Linux for your EC2 instances with `pulumi_easy`.

## Available OS Managers

`pulumi_easy` provides two specialized EC2 manager classes for different operating systems:

1. **EC2Ubuntu** - For creating Ubuntu instances
2. **EC2AL** - For creating Amazon Linux instances

Both extend the base `EC2Manager` class with OS-specific functionality.

## Choosing the Right OS

### Ubuntu

**Best for:**
- Development environments where familiarity with Ubuntu is important
- When you need specific Ubuntu packages or PPAs
- When compatibility with other Debian-based systems is required
- When you need the latest LTS releases with 5-year support cycle

**Available versions:**
- 20.04 LTS (Focal Fossa)
- 22.04 LTS (Jammy Jellyfish)
- 24.04 LTS (Noble Numbat)

**Example:**
```python
import pulumi_easy as easy

ubuntu_manager = easy.EC2Ubuntu()
instance = ubuntu_manager.create_ubuntu_instance(
    name="web-server",
    storage=20,
    version="22.04",  # Ubuntu Jammy
    arch="amd64",
    instance_type="t3.micro",
    ssh_key_name="my-key"
)
```

### Amazon Linux

**Best for:**
- Production workloads on AWS
- Optimized performance on EC2 infrastructure
- Seamless integration with AWS services
- When you need AWS support

**Available versions:**
- Amazon Linux 2 (version="2")
- Amazon Linux 2023 (version="3")

**Example:**
```python
import pulumi_easy as easy

al_manager = easy.EC2AL()
instance = al_manager.create_amazon_linux_instance(
    name="app-server",
    storage=20,
    version="3",  # Amazon Linux 2023
    arch="arm64",
    instance_type="t4g.micro",
    ssh_key_name="my-key"
)
```

## Architecture Options

Both OS types support different CPU architectures:

### For Ubuntu:
- `arch="amd64"` - For x86_64 instances (e.g., t2, t3, m5, c5)
- `arch="arm64"` - For ARM-based Graviton instances (e.g., t4g, c6g, m6g)

### For Amazon Linux:
- `arch="x86_64"` - For x86_64 instances
- `arch="arm64"` - For ARM-based Graviton instances

## Cost Optimization

For cost-effective deployments, consider using:

1. **ARM-based Graviton instances** with matching ARM64 AMIs
   - Typically offer better price-to-performance ratio
   - Example instance families: t4g, c6g, m6g, r6g

2. **Spot instances** (can be used with either OS)
   - Can reduce costs by 70-90% compared to on-demand pricing
   - Good for fault-tolerant workloads

## Complete Comparison Example

Here's a comprehensive example showing both operating systems with equivalent configurations:

```python
import pulumi
import pulumi_easy as easy

# Get user's IP for secure SSH access
ip = easy.get_my_ip()

# Create shared key pair
ec2 = easy.EC2Manager()
key_pair = ec2.create_key_pair(
    name="comparison-key",
    public_key="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@hostname"
)

# Initialize OS-specific managers
ubuntu = easy.EC2Ubuntu()
amazon_linux = easy.EC2AL()

# Create equivalent Ubuntu and Amazon Linux instances
ubuntu_instance = ubuntu.create_ubuntu_instance(
    name="ubuntu-server",
    storage=20,
    version="24.04",  # Ubuntu Noble
    arch="arm64",
    instance_type="t4g.nano",
    ssh_key_name=key_pair.key_name,
    my_ipv4=ip['ipv4']
)

al_instance = amazon_linux.create_amazon_linux_instance(
    name="al-server",
    storage=20,
    version="3",  # Amazon Linux 2023
    arch="arm64",
    instance_type="t4g.nano",
    ssh_key_name=key_pair.key_name,
    my_ipv4=ip['ipv4']
)

# Export the public IPs
pulumi.export("ubuntu_ip", ubuntu_instance.public_ip)
pulumi.export("amazon_linux_ip", al_instance.public_ip)
```

## Additional Considerations

- **Package Management**: Ubuntu uses `apt`, Amazon Linux uses `yum` (AL2) or `dnf` (AL2023)
- **Update Cycles**: Ubuntu has predictable LTS releases; Amazon Linux has rolling releases
- **Default User**: Ubuntu uses `ubuntu`, Amazon Linux uses `ec2-user`
- **Root Device**: Ubuntu typically uses `/dev/sda1`, Amazon Linux uses `/dev/xvda`
- **AWS Integration**: Amazon Linux includes AWS tools and optimizations out of the box

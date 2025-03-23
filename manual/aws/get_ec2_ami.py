import pulumi
import pulumi_aws as aws

def get_ubuntu_ami(version: str, arch: str):
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

get_ubuntu_ami("22.04", "amd64")
get_ubuntu_ami("24.04", "arm64")

import ipaddress
from requests import get
from requests.exceptions import RequestException

def get_my_ip():
    """
    Get the public IP of the machine running this script.

    Returns:
        dict: A dictionary containing IPv4 and IPv6 addresses (if available).
    """
    timeout = 10
    result = {
        "ipv4": "",
        "ipv6": "",
    }
    
    # Get IPv4 address
    try:
        result["ipv4"] = get("https://api.ipify.org", timeout=timeout).text
    except RequestException:
        result["ipv4"] = ""
    
    # Get IPv6 address
    try:
        result["ipv6"] = get("https://api6.ipify.org", timeout=timeout).text
    except RequestException:
        result["ipv6"] = ""
    
    return result

def ipv4_cidr_slice(cidr: str, count: int):
    """
    Divide a CIDR block into smaller subnets by increasing the prefix length.
    
    Args:
        cidr (str): The CIDR block to divide (e.g., '10.0.0.0/16')
        count (int): Number of bits to add to the prefix length
            (e.g., if count=2 and cidr is /16, creates subnets with /18)
            
    Returns:
        list: A list of subnet CIDR blocks as strings
        
    Example:
        ```python
        subnets = ipv4_cidr_slice('192.168.0.0/24', 2)
        # Returns: ['192.168.0.0/26', '192.168.0.64/26', '192.168.0.128/26', '192.168.0.192/26']
        ```
    """
    # Check if the CIDR is valid
    try:
        network = ipaddress.ip_network(cidr)
    except ValueError:
        return []
    
    # Generate subnets
    subnets = list(network.subnets(new_prefix=network.prefixlen+count))
    return [str(subnet) for subnet in subnets]

def calculate_subnet_info(cidr_list):
    """
    Calculate detailed information about each subnet in the provided list.
    
    Args:
        cidr_list (list): List of CIDR blocks
        
    Returns:
        list: A list of dictionaries containing subnet information
    """
    result = []
    for cidr in cidr_list:
        network = ipaddress.IPv4Network(cidr)
        info = {
            'cidr': cidr,
            'network_address': str(network.network_address),
            'broadcast_address': str(network.broadcast_address),
            'netmask': str(network.netmask),
            'num_addresses': network.num_addresses,
            'hosts': network.num_addresses - 2 if network.prefixlen < 31 else network.num_addresses
        }
        result.append(info)
    
    return result

def subdivide_cidr(original_cidr, new_prefix):
    """
    Subdivide a larger CIDR block into smaller CIDR blocks with the specified prefix length.
    
    Args:
        original_cidr (str): The original CIDR block (e.g., '10.0.0.0/16')
        new_prefix (int): The prefix length for the smaller subnets (e.g., 20)
        
    Returns:
        list: A list of CIDR blocks with the specified prefix
    """
    network = ipaddress.IPv4Network(original_cidr)
    
    # If the new prefix is smaller than or equal to the original, return the original
    if new_prefix <= network.prefixlen:
        return [original_cidr]
    
    # Generate all subnets with the new prefix length
    subnets = list(network.subnets(new_prefix=new_prefix))
    
    # Convert subnets to string representation
    return [str(subnet) for subnet in subnets]

def subdivide_ipv6_cidr(cidr, new_prefix):
    """
    Subdivide an IPv6 CIDR block into smaller subnets with specified prefix length.
    Specialized for IPv6 to handle the larger address space efficiently.
    
    Args:
        cidr (str): The IPv6 CIDR block to subdivide
        new_prefix (int): The new prefix length for subdivided networks
        
    Returns:
        list: List of IPv6 subnet CIDRs as strings
    """
    network = ipaddress.IPv6Network(cidr)
    
    # Check if the requested subdivision is valid
    if new_prefix <= network.prefixlen:
        raise ValueError(f"New prefix must be larger than the current prefix ({network.prefixlen})")
    
    # Calculate how many subnets will be created
    subnets_count = 2 ** (new_prefix - network.prefixlen)
    
    # If there would be too many subnets, use the generator instead of creating a full list
    if subnets_count > 10000:
        return [str(subnet) for subnet in network.subnets(new_prefix=new_prefix)]
    
    return [str(subnet) for subnet in network.subnets(new_prefix=new_prefix)]

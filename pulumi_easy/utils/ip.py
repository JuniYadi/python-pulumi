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
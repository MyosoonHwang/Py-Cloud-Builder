import requests
from config import NETWORK_API_URL

def get_headers(token):
    return {'X-Auth-Token': token, 'Content-Type': 'application/json'}

def fetch_vpcs(token):
    try:
        url = f"{NETWORK_API_URL}/v2.0/vpcs"
        return requests.get(url, headers=get_headers(token)).json().get('vpcs', [])
    except Exception as e:
        print(f"❌ VPC 조회 오류: {e}")
        return []

def fetch_subnets(token):
    try:
        url = f"{NETWORK_API_URL}/v2.0/vpcsubnets"
        return requests.get(url, headers=get_headers(token)).json().get('vpcsubnets', [])
    except Exception as e:
        print(f"❌ 서브넷 조회 오류: {e}")
        return []

def create_vpc_api(token, name, cidr):
    url = f"{NETWORK_API_URL}/v2.0/vpcs"
    body = { "vpc": { "name": name, "cidrv4": cidr } }
    return requests.post(url, json=body, headers=get_headers(token))

def create_subnet_api(token, vpc_id, name, cidr):
    url = f"{NETWORK_API_URL}/v2.0/vpcsubnets"
    body = { "vpcsubnet": { "vpc_id": vpc_id, "cidr": cidr, "name": name } }
    return requests.post(url, json=body, headers=get_headers(token))
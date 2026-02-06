import requests
import json
from config import NETWORK_API_URL

def get_headers(token):
    return {'X-Auth-Token': token, 'Content-Type': 'application/json'}

# ==========================================
# VPC & Subnet
# ==========================================
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

# ==========================================
# 🔌 포트 (인스턴스 인터페이스)
# ==========================================
def fetch_ports(token):
    """인스턴스와 연결된 포트 목록 조회"""
    try:
        url = f"{NETWORK_API_URL}/v2.0/ports"
        return requests.get(url, headers=get_headers(token)).json().get('ports', [])
    except Exception as e:
        print(f"❌ 포트 조회 오류: {e}")
        return []

# ==========================================
# 🌐 플로팅 IP (Floating IP)
# ==========================================
def fetch_floating_ips(token):
    try:
        url = f"{NETWORK_API_URL}/v2.0/floatingips"
        return requests.get(url, headers=get_headers(token)).json().get('floatingips', [])
    except Exception as e:
        return []

def create_floating_ip(token, network_id):
    url = f"{NETWORK_API_URL}/v2.0/floatingips"
    body = {
        "floatingip": {
            "floating_network_id": network_id,
            "port_id": None
        }
    }
    return requests.post(url, json=body, headers=get_headers(token))

def associate_floating_ip(token, fip_id, port_id):
    """플로팅 IP를 특정 포트(인스턴스)에 연결/해제"""
    url = f"{NETWORK_API_URL}/v2.0/floatingips/{fip_id}"
    body = {
        "floatingip": {
            "port_id": port_id  # None이면 해제
        }
    }
    return requests.put(url, json=body, headers=get_headers(token))

# ==========================================
# 🛡️ 보안 그룹 (Security Group)
# ==========================================
def fetch_security_groups(token):
    try:
        url = f"{NETWORK_API_URL}/v2.0/security-groups"
        return requests.get(url, headers=get_headers(token)).json().get('security_groups', [])
    except: return []

def create_security_group(token, name, description):
    url = f"{NETWORK_API_URL}/v2.0/security-groups"
    body = {
        "security_group": {
            "name": name,
            "description": description
        }
    }
    return requests.post(url, json=body, headers=get_headers(token))

def create_security_group_rule(token, sg_id, protocol, port, remote_ip_prefix):
    """보안 그룹 규칙 추가 (TCP 22 허용 등)"""
    url = f"{NETWORK_API_URL}/v2.0/security-group-rules"
    body = {
        "security_group_rule": {
            "security_group_id": sg_id,
            "direction": "ingress",
            "protocol": protocol,
            "port_range_min": port,
            "port_range_max": port,
            "remote_ip_prefix": remote_ip_prefix,
            "ethertype": "IPv4"
        }
    }
    return requests.post(url, json=body, headers=get_headers(token))
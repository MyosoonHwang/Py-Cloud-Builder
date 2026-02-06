import ipaddress

def validate_cidr(cidr_text, vpc_cidr=None):
    """
    CIDR 형식이 올바른지, 그리고 VPC 대역(vpc_cidr) 내부에 포함되는지 검증
    """
    try:
        subnet_net = ipaddress.IPv4Network(cidr_text)
        if vpc_cidr and not subnet_net.subnet_of(ipaddress.IPv4Network(vpc_cidr)):
            print(f"   ❌ 범위 오류: VPC({vpc_cidr}) 밖입니다.")
            return None
        return str(subnet_net)
    except ValueError:
        return None
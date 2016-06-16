import os
import re

def get_arp_table():
    arp_table = filter(lambda x: x != '',
                       os.popen('arp -a').read().split('\n'))
    arp_dict = dict()
    for row in arp_table:
        ip = re.search(r'\d+\.\d+\.\d+\.\d+', row)
        mac = re.search(r'..:..:..:..:..:..', row)
        if mac is None:
            continue
        arp_dict[ip.group(0)] = mac.group(0)
    return arp_dict
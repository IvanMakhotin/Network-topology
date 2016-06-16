
import os
import re

#ip = '172.19.0.3' 
#oid = '.1.3.6.1.2.1.17.4.3.1.2' mac address table oid

def get_mac_table(ip):
    oid = '.1.3.6.1.2.1.17.4.3.1.2'
    mac_table = filter(lambda x: x != '',
                       os.popen('snmpwalk -Cc -v 2c -c public ' + ip + ' ' + oid).read().split('\n'))
    
    print "mac table has been collected" 
    if not mac_table:
        return mac_table

    mac_dict = dict()
    for (i, row) in enumerate(mac_table):
        port = re.search(r'[0-9]+$', row)
        mac = re.search(r'\d+\.\d+\.\d+\.\d+\.\d+\.\d+ =', row)
        if mac is None or port is None:
            print row
            continue
        mac_hex_list = [str(hex(int(e)))[2:] for e in mac.group(0)[:-2].split('.')]
        for (i, e) in enumerate(mac_hex_list):
          if len(e) == 1:
            mac_hex_list[i] = '0' + mac_hex_list[i]

        mac_dict[':'.join(mac_hex_list)] = port.group(0) 
    return mac_dict

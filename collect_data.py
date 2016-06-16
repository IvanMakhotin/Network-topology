import re
import os
import time
from get_arp_table import get_arp_table
from get_mac_table import get_mac_table
from thread_pinger import ping_ips


with open('ip.txt', 'r') as f:
    ips = f.readlines()

ips = [ip[:-1] for ip in ips]


ips_by_mask = ['172.19.' + str(i) + '.' + str(j) for i in list(list(range(4)) + list(range(130,135)) + list(range(170,177))) for j in range(256)]
#ips_by_mask.remove('172.19.0.0')
#ips_by_mask.remove('172.19.255.255')

succsess_ping = list()
arp_table = get_arp_table()

for i in range(0, len(ips_by_mask), 50):
	succsess_ping += ping_ips(ips_by_mask[i:i+50])
	arp_table.update(get_arp_table())
	time.sleep(5)

print str(len(succsess_ping)) + " devices has been pinged succsessful"
print "ping them one more time"

time.sleep(30)
ping_ips(succsess_ping)


mac_tables = list()
ping_ips(ips)
for ip in ips:
    print "Start hadle next ip:", ip
    mac_tables.append({ip : get_mac_table(ip)})

with open('arp_table.txt', 'w+') as arp, open('mac_tables.txt', 'w+') as mac:
    arp.write(str(arp_table))
    mac.write(str(mac_tables))


import itertools
import networkx as nx
import matplotlib.pyplot as plt
import pylab

def union(*dicts):
    return dict(itertools.chain(*map(lambda dct: list(dct.items()), dicts)))

with open('arp_table.txt', 'r') as arp, open('mac_tables.txt', 'r') as mac:
     mac_tables = eval(mac.read())
     arp_table = eval(arp.read())

mac_tables = union(*mac_tables)
ips_in_arp = set(arp_table.keys())
inv_arp_table = {v: k for k, v in arp_table.items()}
ips_with_mac_table = set(mac_tables.keys())
managed_switches_ips = [ip for ip in ips_in_arp.intersection(ips_with_mac_table) if mac_tables[ip]]

mac_table_by_mac = dict()
inv_mac_table_by_mac = dict()
for ip in managed_switches_ips:
    inv_mac_table = {}
    for k, v in mac_tables[ip].iteritems():
        inv_mac_table[v] = inv_mac_table.get(v, [])
        inv_mac_table[v].append(k)
    mac_table_by_mac[arp_table[ip]] = inv_mac_table
    inv_mac_table_by_mac[arp_table[ip]] = mac_tables[ip] 

def it_is_switch(mac_address):
    return mac_address in mac_table_by_mac.keys()

def get_switches(addresses):
    mask = map(it_is_switch, addresses)
    return list(itertools.compress(addresses, mask))

def get_another_switch_addresses_intersection(switch_mac_addr, current_port, another_switch_mac_addr):
    another_switch_port = inv_mac_table_by_mac[another_switch_mac_addr].get(switch_mac_addr)
    #################
    physicaly_connected_pcs = []
    for current_port in mac_table_by_mac[switch_mac_addr].keys():
        addresses_by_port = mac_table_by_mac[switch_mac_addr][current_port]
        connected_switches = get_switches(addresses_by_port)
        if len(addresses_by_port) >= 1 and not connected_switches:
            physicaly_connected_pcs += addresses_by_port

    for pc in physicaly_connected_pcs:
        if another_switch_port is None:
            another_switch_port = inv_mac_table_by_mac[another_switch_mac_addr].get(pc)
        else:
            break
    #################

    if another_switch_port is None:
        print 'Error: SOSED NE ZNAET SOSEDA'        
        return list()
    print 'OK'
    addresses_by_another_port = mac_table_by_mac[another_switch_mac_addr][another_switch_port]
    addresses_by_port = mac_table_by_mac[switch_mac_addr][current_port]
    addresses_intersection = list(set(addresses_by_another_port).intersection(set(addresses_by_port)))
    return addresses_intersection

#pc_no = 0
hub_no = 0
marked_swtches = list()
G = nx.Graph()
#val_map = {'hub_no0': 0.0}
val_map = dict()
HUB_COL = 55.0
PC_COL = 100.0
SW_COL = 0.0

def name_by_mac(mac):
    if inv_arp_table.get(mac) is None:
        return mac
    else:
        return inv_arp_table[mac]

######################################################
with  open('mac_tables_by_mac_dict.txt', 'w') as mac_dict:
    mac_dict.write(str(mac_table_by_mac))
######################################################

for switch_mac_addr in mac_table_by_mac.keys():

    val_map[name_by_mac(switch_mac_addr)] = SW_COL
    for current_port in mac_table_by_mac[switch_mac_addr].keys():
        addresses_by_port = mac_table_by_mac[switch_mac_addr][current_port]
        connected_switches = get_switches(addresses_by_port)
        #connected_switches = [switch for switch in connected_switches if switch not in marked_swtches]

        if len(addresses_by_port) == 1 and not connected_switches:
            G.add_edge(name_by_mac(switch_mac_addr), name_by_mac(addresses_by_port[0]))
            val_map[name_by_mac(addresses_by_port[0])] = PC_COL
            #G.add_edge(switch_mac_addr, "pc_no" + str(pc_no))
            #pc_no += 1
        if len(addresses_by_port) > 1 and not connected_switches:
            G.add_edge(name_by_mac(switch_mac_addr), "hub_no" + str(hub_no))
            val_map['hub_no' + str(hub_no)] = HUB_COL
            for pc in addresses_by_port:
                G.add_edge("hub_no" + str(hub_no), name_by_mac(pc))
                val_map[name_by_mac(pc)] = PC_COL
            hub_no += 1
        if len(connected_switches) == 1:
            another_switch_mac_addr = connected_switches[0]
            addresses_intersection = get_another_switch_addresses_intersection(switch_mac_addr, current_port, another_switch_mac_addr)
            if addresses_intersection:
                G.add_edge(name_by_mac(switch_mac_addr), "hub_no" + str(hub_no))
                val_map['hub_no' + str(hub_no)] = HUB_COL
                G.add_edge(name_by_mac(another_switch_mac_addr), "hub_no" + str(hub_no))
                for pc in addresses_intersection:
                    G.add_edge("hub_no" + str(hub_no), name_by_mac(pc))
                    val_map[name_by_mac(pc)] = PC_COL
                hub_no += 1
            else:
                G.add_edge(name_by_mac(switch_mac_addr), name_by_mac(another_switch_mac_addr))
        if len(connected_switches) > 1:
            intersections = list()
            for another_switch_mac_addr in connected_switches:
                addresses_intersection = get_another_switch_addresses_intersection(switch_mac_addr, current_port, another_switch_mac_addr)
                intersections.append(addresses_intersection)

            if all(intersections):
                intersections = map(set, intersections)
                intersection = set.intersection(*intersections)
                G.add_edge(name_by_mac(switch_mac_addr), "hub_no" + str(hub_no))
                val_map['hub_no' + str(hub_no)] = HUB_COL
                for another_switch_mac_addr in connected_switches:
                    G.add_edge(name_by_mac(another_switch_mac_addr), "hub_no" + str(hub_no))
                for pc in intersection:
                    G.add_edge("hub_no" + str(hub_no), name_by_mac(pc))
                    val_map[name_by_mac(pc)] = PC_COL
                hub_no += 1
            else:
                another_switch_mac_addr = connected_switches[intersections.index(list())]
                G.add_edge(name_by_mac(switch_mac_addr), name_by_mac(another_switch_mac_addr))
        marked_swtches.append(switch_mac_addr)


'''
for i in range(hub_no):
    val_map['hub_no' + str(i)] = 55.0
for i in range(pc_no):
    val_map['pc_no' + str(i)] = 100.0
for switch_mac_addr in mac_table_by_mac.keys():
    val_map[switch_mac_addr] = 0.0
'''
values = [val_map.get(node, 0.1) for node in G.nodes()]
nx.draw(G, cmap=plt.get_cmap('jet'), node_color=values, with_labels=True)
pylab.show()
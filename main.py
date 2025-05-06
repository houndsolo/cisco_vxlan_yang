#!/usr/bin/env python3
import time
from inventory.vars import *
from inventory.vyos_leafs import *

from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit, netconf_validate
from nornir_utils.plugins.functions import print_result

from tasks.netconf_locks        import  global_lock, global_unlock
from tasks.set_system_settings  import  system_config_payload, system_vlan_payload
from tasks.set_p2p_links        import  set_p2p_links
from tasks.set_bgp              import  set_bgp


def configure_vxlan(task,num_leafs,num_spines):


    # rest of evpn vxlan config
    task.run(task=global_lock)

    """
    System config
    - mtu
    - snmp
    - monitoring svi/vlan
    - spanning tree
    - banner
    - non-cisco transcievers
    """
    task.run(
        task=system_config_payload,
    )
    """
    Underlay
    - IPv4 OSPF
    - 10.240.{leaf_id}{spine_id}.0/31
    - PIM-Sparse Mode
    - Loopback0 - iBGP peering
    - Loopback2 - VTEP peering
    """
    task.run(
        task=set_p2p_links,
        num_spines=num_spines,
        num_leafs=num_leafs
    )
    """
    Overlay
    - iBGP
    """
    task.run(
        task=set_bgp,
        num_spines=num_spines,
        num_leafs=num_leafs
    )

    task.run(netconf_validate)
    task.run(netconf_commit, manager=task.host["manager"])

    task.run(task=global_unlock)

    """
    do vlans separately?
    need EVPN profile configured first before adding VLAN to EVPN-Member
    """
    #time.sleep(3)

    ## set vlans last, EVI instance needs to be configured first
    #task.run(task=global_lock)
    #task.run(task=system_vlan_payload)
    #task.run(netconf_validate)
    #task.run(netconf_commit, manager=task.host["manager"])
    #task.run(task=global_unlock)

def main():
    nr = InitNornir(config_file="config.yml")
#    nr_spines = nr.filter(F(groups__contains="spine"))
    nr_leafs = nr.filter(F(groups__contains="leaf"))
#    nr_s7 = nr.filter(hostname="10.20.0.7")

    results = nr.run(task=configure_vxlan, num_spines=num_spines, num_leafs=num_leafs)
    print_result(results)

if __name__ == "__main__":
    main()

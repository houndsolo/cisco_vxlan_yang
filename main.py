#!/usr/bin/env python3

from inventory.vars import *
from inventory.vyos_leafs import *

from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit, netconf_validate
from nornir_utils.plugins.functions import print_result

from tasks.netconf_locks        import  global_lock, global_unlock
from tasks.set_system_settings  import  system_config_payload
from tasks.set_bgp_leaf         import  set_bgp_leaf
from tasks.set_bgp_spine        import  set_bgp_spine
from tasks.set_p2p_links_leaf   import  set_p2p_links_leaf
from tasks.set_p2p_links_spine  import  set_p2p_links_spine

def configure_vxlan_leafs(task,num_spines):
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
        task=set_p2p_links_leaf,
        num_spines=num_spines
    )
    """
    Overlay
    - iBGP
    - L2VPN EVPN
    """
    task.run(
        task=set_bgp_leaf,
        num_spines=num_spines
    )

    task.run(netconf_validate)
    task.run(netconf_commit, manager=task.host["manager"])

    task.run(task=global_unlock)

def configure_vxlan_spines(task,num_leafs):
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
        task=set_p2p_links_spine,
        num_leafs=num_leafs
    )
    """
    Overlay
    - iBGP
    """
    task.run(
        task=set_bgp_spine,
        num_leafs=num_leafs
    )

    task.run(netconf_validate)
    task.run(netconf_commit, manager=task.host["manager"])

    task.run(task=global_unlock)

def main():
    # Initialize Nornir with your config.yaml pointing at inventory/*
    nr = InitNornir(config_file="config.yml")
    nr_spines = nr.filter(F(groups__contains="spine"))
    nr_leafs = nr.filter(F(groups__contains="leaf"))

    leaf_results = nr_leafs.run(task=configure_vxlan_leafs, num_spines=num_spines)
    print_result(leaf_results)

    spine_results = nr_spines.run(task=configure_vxlan_spines, num_leafs=num_leafs)
    print_result(spine_results)

if __name__ == "__main__":
    main()

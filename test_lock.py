#!/usr/bin/env python3
from inventory.vars import *
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit
from nornir_utils.plugins.functions import print_result

from tasks.set_system_settings  import  system_config_payload
from tasks.set_bgp_leaf         import  set_bgp_leaf
from tasks.set_bgp_spine        import  set_bgp_spine
from tasks.set_p2p_links_leaf   import  set_p2p_links_leaf
from tasks.set_p2p_links_spine  import  set_p2p_links_spine


def configure_vxlan_leafs(task,num_spines):
    task.run(
        task=system_config_payload,
    )
    task.run(
        task=set_p2p_links_leaf,
        num_spines=num_spines
    )
    task.run(
        task=set_bgp_leaf,
        num_spines=num_spines
    )

def configure_vxlan_spines(task,num_leafs):
    task.run(
        task=system_config_payload,
    )
    task.run(
        task=set_p2p_links_spine,
        num_leafs=num_leafs
    )
    task.run(
        task=set_bgp_spine,
        num_leafs=num_leafs
    )

def global_lock(task):
    lock = task.run(netconf_lock, datastore="candidate", operation="lock")
    task.host["manager"] = lock.result.manager

def global_unlock(task):
    task.run(netconf_lock, datastore="candidate", operation="unlock", manager=task.host["manager"])

def main():
    # Initialize Nornir with your config.yaml pointing at inventory/*
    nr = InitNornir(config_file="config.yml")
    nr_spines = nr.filter(F(groups__contains="spine"))
    nr_leafs = nr.filter(F(groups__contains="leaf"))

    print_result(nr_leafs.run(task=global_lock))

    spine_results = nr_spines.run(task=configure_vxlan_spines, num_leafs=num_leafs)
    print_result(spine_results)

    print_result(nr_leafs.run(task=global_unlock))

if __name__ == "__main__":
    main()

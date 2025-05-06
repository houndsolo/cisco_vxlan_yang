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
from tasks.set_p2p_links        import  set_p2p_links
from tasks.set_bgp              import  set_bgp


def configure_vxlan(task,num_leafs,num_spines):
    task.run(task=global_lock)
    task.run(
        task=system_config_payload,
    )
    task.run(netconf_validate)
    task.run(netconf_commit, manager=task.host["manager"])

    task.run(task=global_unlock)

def main():
    nr = InitNornir(config_file="config.yml")
#    nr_spines = nr.filter(F(groups__contains="spine"))
    nr_leafs = nr.filter(F(groups__contains="leaf"))
#    nr_s7 = nr.filter(hostname="10.20.0.7")

    results = nr_leafs.run(task=configure_vxlan, num_spines=num_spines, num_leafs=num_leafs)
    print_result(results)

if __name__ == "__main__":
    main()

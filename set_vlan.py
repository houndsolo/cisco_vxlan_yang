#!/usr/bin/env python3
import time
from inventory.vars import *
from inventory.vyos_leafs import *

from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit, netconf_validate
from nornir_utils.plugins.functions import print_result

from tasks.netconf_locks        import  global_lock, global_unlock
from tasks.set_system_settings  import  system_vlan_payload


def configure_vxlan(task,num_leafs,num_spines):

    """
    do vlans separately?
    need EVPN profile configured first before adding VLAN to EVPN-Member
    """

    # set vlans last, EVI instance needs to be configured first
    task.run(task=global_lock)
    task.run(task=system_vlan_payload)
    task.run(netconf_validate)
    task.run(netconf_commit, manager=task.host["manager"])
    task.run(task=global_unlock)

def main():
    nr = InitNornir(config_file="config.yml")

    results = nr.run(task=configure_vxlan, num_spines=num_spines, num_leafs=num_leafs)
    print_result(results)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from inventory.vars import *
from set_banner import system_config_payload
from set_p2p_links_leaf import set_p2p_links
from set_bgp_leaf import set_bgp

from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit
from nornir_utils.plugins.functions import print_result

def main():
    nr = InitNornir(config_file="config.yml")
    nr_spines = nr.filter(F(groups__contains="spine"))
    nr_leafs = nr.filter(F(groups__contains="leaf"))
    nr_s7 = nr.filter(hostname="10.20.0.7")
    nr_s10 = nr.filter(hostname="10.20.0.10")

    ### all  ###
    # system configuration
    results = nr_leafs.run(task=system_config_payload)
    print_result(results)

    #### leaf config  zzzz
    # p2p links
    results = nr_leafs.run(
        task=set_p2p_links,
        num_spines=num_spines
    )
    print_result(results)

    # set bgp
    results = nr_leafs.run(
        task=set_bgp,
        num_spines=num_spines
    )
    print_result(results)


if __name__ == "__main__":
    main()

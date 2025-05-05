#!/usr/bin/env python3
from inventory.vars import *
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit
from nornir_utils.plugins.functions import print_result


# Define the number of spines. This could also come from Nornir inventory.

def set_bgp(task, num_spines):
    """
    Configures point-to-point links on leaf switches connecting to spines.
    Assumes interfaces are TenGigabitEthernet1/0/1, 1/0/2, etc.,
    corresponding to Spine 1, Spine 2, etc.
    Assigns unique IP addresses based on leaf node_id and spine index.
    """
    leaf_node_id = task.host["node_id"]
    bgp_neighbor_base_combined = [] # List to hold XML config for each interface
    bgp_neighbor_l2vpn_evpn_combined = []

    for vyos_leaf in vyos_leafs:
        # Construct XML payload fragment for this specific interface
        bgp_neighbor_base_config = f"""
              <neighbor>
                <id>10.240.254.{vyos_leaf['node_id']}</id>
                <remote-as>700</remote-as>
                <ebgp-multihop-v2>
                  <enable/>
                  <max-hop>4</max-hop>
                </ebgp-multihop-v2>
                <ebgp-multihop>
                  <max-hop>4</max-hop>
                </ebgp-multihop>
                <update-source>
                  <interface>
                    <Loopback>0</Loopback>
                  </interface>
                </update-source>
              </neighbor>
        """
        bgp_neighbor_base_combined.append(bgp_neighbor_base_config)
        bgp_neighbor_l2vpn_evpn_config = f"""
                      <neighbor>
                        <id>10.240.254.{vyos_leaf['node_id']}</id>
                        <activate/>
                        <route-reflector-client/>
                        <send-community-v2>
                          <send-community-where>both</send-community-where>
                        </send-community-v2>
                        <send-community>
                          <send-community-where>both</send-community-where>
                        </send-community>
                        <soft-reconfiguration>inbound</soft-reconfiguration>
                      </neighbor>
        """
        bgp_neighbor_l2vpn_evpn_combined.append(bgp_neighbor_l2vpn_evpn_config)

    for leaf_index in range(num_leafs):
        # Construct XML payload fragment for this specific interface
        bgp_neighbor_base_config = f"""
              <neighbor>
                <id>10.240.254.{leaf_index + 1}</id>
                <remote-as>700</remote-as>
                <ebgp-multihop-v2>
                  <enable/>
                  <max-hop>4</max-hop>
                </ebgp-multihop-v2>
                <ebgp-multihop>
                  <max-hop>4</max-hop>
                </ebgp-multihop>
                <update-source>
                  <interface>
                    <Loopback>0</Loopback>
                  </interface>
                </update-source>
              </neighbor>
        """
        bgp_neighbor_base_combined.append(bgp_neighbor_base_config)

        bgp_neighbor_l2vpn_evpn_config = f"""
                      <neighbor>
                        <id>10.240.254.{leaf_index + 1}</id>
                        <activate/>
                        <route-reflector-client/>
                        <send-community-v2>
                          <send-community-where>both</send-community-where>
                        </send-community-v2>
                        <send-community>
                          <send-community-where>both</send-community-where>
                        </send-community>
                        <soft-reconfiguration>inbound</soft-reconfiguration>
                      </neighbor>
        """
        bgp_neighbor_l2vpn_evpn_combined.append(bgp_neighbor_l2vpn_evpn_config)

    full_config_payload = f"""
      <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
          <router>
            <bgp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-bgp">
              <id>700</id>
              <bgp>
                <default>
                  <ipv4-unicast>false</ipv4-unicast>
                  <route-target>
                    <filter>false</filter>
                  </route-target>
                </default>
                <log-neighbor-changes>true</log-neighbor-changes>
              </bgp>
          {''.join(bgp_neighbor_base_combined)}
              <address-family>
                <no-vrf>
                  <ipv4>
                    <af-name>unicast</af-name>
                  </ipv4>
                  <l2vpn>
                    <af-name>evpn</af-name>
                    <l2vpn-evpn>
          {''.join(bgp_neighbor_l2vpn_evpn_combined)}
                    </l2vpn-evpn>
                  </l2vpn>
                </no-vrf>
              </address-family>
            </bgp>
          </router>
        </native>
      </config>
    """

    result = task.run(netconf_edit_config, config=full_config_payload, target="running")



def main():
    # Initialize Nornir with your config.yaml pointing at inventory/*
    # Make sure your inventory (e.g., inventory/hosts.yml) includes:
    # 1. Devices in the 'leaf' group
    # 2. A 'node_id' data variable for each leaf (e.g., node_id: 1)
    nr = InitNornir(config_file="config.yml")

    # Filter for leaf devices
    nr_spines = nr.filter(F(groups__contains="spine"))
    nr_s8 = nr.filter(hostname="10.20.0.8")

    # Define the number of spines (can be made dynamic via inventory/config)

    # Run the task on the filtered leaf devices, passing the number of spines
    results = nr_s8.run(
        task=set_bgp,
        num_spines=num_spines
    )

    # Display the results
    print_result(results)


if __name__ == "__main__":
    main()

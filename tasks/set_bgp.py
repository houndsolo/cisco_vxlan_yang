#!/usr/bin/env python3
from inventory.vars import *
from inventory.vyos_leafs import *
from tasks.netconf_locks import *
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit, netconf_validate
from nornir_utils.plugins.functions import print_result


# Define the number of spines. This could also come from Nornir inventory.

def set_bgp(task, num_spines, num_leafs):
    node_id = task.host["node_id"]
    bgp_neighbor_base_combined = []
    bgp_neighbor_l2vpn_evpn_combined = []

    if "leaf" in task.host.groups:
        for spine_index in range(num_spines):
            spine_bgp_peering_ip = f"10.240.255.{spine_index + 1}"

            bgp_neighbor_base_config = f"""
                  <neighbor>
                    <id>{spine_bgp_peering_ip}</id>
                    <remote-as>{bgp_spine_as}</remote-as>
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
                            <id>{spine_bgp_peering_ip}</id>
                            <activate/>
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

        #evpn config
        l2vpn_evpn_config = f"""
              <l2vpn>
                <evpn_cont xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-l2vpn">
                  <evpn>
                    <replication-type>
                      <ingress/>
                    </replication-type>
                    <route-target>
                      <auto>
                        <vni/>
                      </auto>
                    </route-target>
                  </evpn>
                  <l2-profile>
                    <evpn>
                      <profile>
                        <default>
                          <l2vni-base>{l2vni_base_default}</l2vni-base>
                        </default>
                      </profile>
                    </evpn>
                  </l2-profile>
                </evpn_cont>
              </l2vpn>
        """
        # network virtualization enpoint config
        nve_interface_configuration = """
              <interface>
                <nve>
                  <name>1</name>
                  <host-reachability>
                    <protocol>
                      <bgp/>
                    </protocol>
                  </host-reachability>
                  <source-interface>
                    <Loopback>0</Loopback>
                  </source-interface>
                </nve>
              </interface>
        """
    elif "spine" in task.host.groups:
        for vyos_leaf in vyos_leafs:
            vyos_bgp_peer_ip = f"10.240.254.{vyos_leaf['node_id']}"
            bgp_neighbor_base_config = f"""
                  <neighbor>
                    <id>{vyos_bgp_peer_ip}</id>
                    <remote-as>{bgp_leaf_as}</remote-as>
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
                            <id>{vyos_bgp_peer_ip}</id>
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
            leaf_bgp_peer_ip = f"10.240.254.{leaf_index + 1}"
            bgp_neighbor_base_config = f"""
                  <neighbor>
                    <id>{leaf_bgp_peer_ip}</id>
                    <remote-as>{bgp_leaf_as}</remote-as>
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
                            <id>{leaf_bgp_peer_ip}</id>
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
          {locals().get("nve_interface_configuration", "")}
          {locals().get("l2vpn_evpn_config", "")}
          <router>
            <bgp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-bgp">
              <id>{bgp_as}</id>
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


    result = task.run(netconf_edit_config, config=full_config_payload, target="candidate")



def main():
    nr = InitNornir(config_file="config.yml")

    results = nr.run(
        task=set_bgp,
        num_spines=num_spines,
        num_leafs=num_leafs
    )

    print_result(results)


if __name__ == "__main__":
    main()

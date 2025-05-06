#!/usr/bin/env python3
from inventory.vars import *
from inventory.vyos_leafs import *
from tasks.netconf_locks import *
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit, netconf_validate
from nornir_utils.plugins.functions import print_result


def set_p2p_links(task, num_spines, num_leafs):
    node_id = task.host["node_id"]
    config_fragments = []

    if "leaf" in task.host.groups:
        loopback_ip = f"10.240.254.{node_id}"
        loopback_ip2 = f"10.240.250.{node_id}"
    elif "spine" in task.host.groups:
        loopback_ip = f"10.240.255.{node_id}"
        loopback_ip2 = f"10.240.253.{node_id}"
    else:
        loopback_ip = "10.255.1.1"  # fallback or raise error
        loopback_ip2 = f"10.240.250.{node_id}"

    p2p_ip_mask = "255.255.255.254"
    loopback_mask = "255.255.255.255"

    if "leaf" in task.host.groups:
        for spine_index in range(num_spines):
            interface_port = spine_index + 1
            leaf_p2p_ip = f"10.240.{node_id}{spine_index+1}.1"

            interface_xml_fragment = f"""
                <TenGigabitEthernet>
                  <name>1/0/{interface_port}</name> <!-- Use standard slot/module/port format -->
                  <description>p2p link to spine {interface_port}</description>
                  <switchport-conf>
                    <switchport>false</switchport>
                  </switchport-conf>
                  <ip>
                    <address>
                      <primary>
                        <address>{leaf_p2p_ip}</address>
                        <mask>{p2p_ip_mask}</mask>
                      </primary>
                    </address>
                    <router-ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
                      <ospf>
                        <process-id>
                          <id>1</id>
                          <area>
                            <area-id>0</area-id>
                          </area>
                        </process-id>
                        <network>
                          <point-to-point/>
                        </network>
                      </ospf>
                    </router-ospf>
                    <pim>
                      <pim-mode-choice-cfg xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-multicast">
                        <sparse-mode/>
                      </pim-mode-choice-cfg>
                    </pim>
                  </ip>
                </TenGigabitEthernet>
            """
            config_fragments.append(interface_xml_fragment)

        loopback_config = f"""
           <Loopback>
             <name>0</name>
             <description>iBGP peering</description>
             <ip>
               <address>
                 <primary>
                   <address>{loopback_ip}</address>
                   <mask>{loopback_mask}</mask>
                 </primary>
               </address>
               <router-ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
                 <ospf>
                   <process-id>
                     <id>1</id>
                     <area>
                       <area-id>0</area-id>
                     </area>
                   </process-id>
                   <network>
                     <point-to-point/>
                   </network>
                 </ospf>
               </router-ospf>
               <pim>
                 <pim-mode-choice-cfg xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-multicast">
                   <sparse-mode/>
                 </pim-mode-choice-cfg>
               </pim>
             </ip>
           </Loopback>
           <Loopback>
             <name>2</name>
             <description>uh...</description>
             <ip>
               <address>
                 <primary>
                   <address>{loopback_ip2}</address>
                   <mask>{loopback_mask}</mask>
                 </primary>
               </address>
               <router-ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
                 <ospf>
                   <process-id>
                     <id>1</id>
                     <area>
                       <area-id>0</area-id>
                     </area>
                   </process-id>
                   <network>
                     <point-to-point/>
                   </network>
                 </ospf>
               </router-ospf>
               <pim>
                 <pim-mode-choice-cfg xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-multicast">
                   <sparse-mode/>
                 </pim-mode-choice-cfg>
               </pim>
             </ip>
           </Loopback>
        """
        config_fragments.append(loopback_config)

    elif "spine" in task.host.groups:
        for vyos_leaf in vyos_leafs:

            spine_p2p_ip = f"10.240.{vyos_leaf['node_id']}{node_id}.0"

            for connection in vyos_leaf["spine_connections"]:
                if connection["spine_id"] == node_id:
                    vyos_leaf_fragment = f"""
                        <TenGigabitEthernet>
                          <name>{connection['interface']}</name>
                          <description>p2p link to leaf {vyos_leaf['hostname']}</description>
                          <switchport-conf>
                            <switchport>false</switchport>
                          </switchport-conf>
                          <ip>
                            <address>
                              <primary>
                                <address>{spine_p2p_ip}</address>
                                <mask>{p2p_ip_mask}</mask>
                              </primary>
                            </address>
                            <router-ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
                              <ospf>
                                <process-id>
                                  <id>1</id>
                                  <area>
                                    <area-id>0</area-id>
                                  </area>
                                </process-id>
                                <network>
                                  <point-to-point/>
                                </network>
                              </ospf>
                            </router-ospf>
                            <pim>
                              <pim-mode-choice-cfg xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-multicast">
                                <sparse-mode/>
                              </pim-mode-choice-cfg>
                            </pim>
                          </ip>
                        </TenGigabitEthernet>
                    """
                    config_fragments.append(vyos_leaf_fragment)
                    break

        # Construct XML payload fragment for this specific interface
        for leaf_index in range(num_leafs):
            interface_port = leaf_index + 1
            spine_p2p_ip = f"10.240.{leaf_index+1}{node_id}.0"

            interface_xml_fragment = f"""
                <TenGigabitEthernet>
                  <name>1/0/{interface_port}</name>
                  <description>p2p link to leaf {interface_port}</description>
                  <switchport-conf>
                    <switchport>false</switchport>
                  </switchport-conf>
                  <ip>
                    <address>
                      <primary>
                        <address>{spine_p2p_ip}</address>
                        <mask>{p2p_ip_mask}</mask>
                      </primary>
                    </address>
                    <router-ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
                      <ospf>
                        <process-id>
                          <id>1</id>
                          <area>
                            <area-id>0</area-id>
                          </area>
                        </process-id>
                        <network>
                          <point-to-point/>
                        </network>
                      </ospf>
                    </router-ospf>
                    <pim>
                      <pim-mode-choice-cfg xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-multicast">
                        <sparse-mode/>
                      </pim-mode-choice-cfg>
                    </pim>
                  </ip>
                </TenGigabitEthernet>
            """
            config_fragments.append(interface_xml_fragment)

        loopback_config = f"""
           <Loopback>
             <name>0</name>
             <description>iBGP peering</description>
             <ip>
               <address>
                 <primary>
                   <address>{loopback_ip}</address>
                   <mask>{loopback_mask}</mask>
                 </primary>
               </address>
               <router-ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
                 <ospf>
                   <process-id>
                     <id>1</id>
                     <area>
                       <area-id>0</area-id>
                     </area>
                   </process-id>
                   <network>
                     <point-to-point/>
                   </network>
                 </ospf>
               </router-ospf>
               <pim>
                 <pim-mode-choice-cfg xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-multicast">
                   <sparse-mode/>
                 </pim-mode-choice-cfg>
               </pim>
             </ip>
           </Loopback>
           <Loopback>
             <name>2</name>
             <description>uh...</description>
             <ip>
               <address>
                 <primary>
                   <address>{loopback_ip2}</address>
                   <mask>{loopback_mask}</mask>
                 </primary>
               </address>
               <router-ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
                 <ospf>
                   <process-id>
                     <id>1</id>
                     <area>
                       <area-id>0</area-id>
                     </area>
                   </process-id>
                   <network>
                     <point-to-point/>
                   </network>
                 </ospf>
               </router-ospf>
               <pim>
                 <pim-mode-choice-cfg xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-multicast">
                   <sparse-mode/>
                 </pim-mode-choice-cfg>
               </pim>
             </ip>
           </Loopback>
        """
        config_fragments.append(loopback_config)



    full_config_payload = f"""
      <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
          <router>
            <router-ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
              <ospf>
                <process-id>
                  <id>1</id>
                  <redistribute>
                    <bgp>
                      <as>{bgp_as}</as>
                    </bgp>
                  </redistribute>
                  <router-id>{loopback_ip}</router-id>
                </process-id>
              </ospf>
            </router-ospf>
          </router>
          <interface>
          {''.join(config_fragments)}
          </interface>
        </native>
      </config>
    """



    result = task.run(netconf_edit_config, config=full_config_payload, target="candidate")



def main():
    nr = InitNornir(config_file="config.yml")

    results = nr.run(
        task=set_p2p_links,
        num_spines=num_spines,
        num_leafs=num_leafs
    )

    print_result(results)

if __name__ == "__main__":
    main()

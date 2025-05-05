#!/usr/bin/env python3
from inventory.vars import *
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit
from nornir_utils.plugins.functions import print_result


# Define the number of spines. This could also come from Nornir inventory.

def set_p2p_links(task, num_leafs):
    """
    Configures point-to-point links on leaf switches connecting to spines.
    Assumes interfaces are TenGigabitEthernet1/0/1, 1/0/2, etc.,
    corresponding to Spine 1, Spine 2, etc.
    Assigns unique IP addresses based on leaf node_id and spine index.
    """
    spine_node_id = task.host["node_id"]
    leaf_interface_snippet = [] # List to hold XML config for each interface

    for leaf_index in range(num_leafs):
        interface_port = leaf_index + 1
        spine_p2p_ip = f"10.240.{leaf_index+1}{spine_node_id}.0"
        spine_loopback_ip = f"10.240.255.{spine_node_id}"  #BGP
        spine_loopback_ip2 = f"10.240.253.{spine_node_id}" #MSDP
        p2p_ip_mask = "255.255.255.254"

        # Construct XML payload fragment for this specific interface
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
        leaf_interface_snippet.append(interface_xml_fragment)

    loopback_config = f"""
       <Loopback>
         <name>0</name>
         <description>ibgp peering</description>
         <ip>
           <address>
             <primary>
               <address>{spine_loopback_ip}</address>
               <mask>255.255.255.255</mask>
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
               <address>{spine_loopback_ip2}</address>
               <mask>255.255.255.255</mask>
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

    # Combine all interface fragments into one complete config payload
    # The <interface> tag itself can contain multiple interface definitions
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
                      <as>700</as>
                    </bgp>
                  </redistribute>
                  <router-id>{spine_loopback_ip}</router-id>
                </process-id>
              </ospf>
            </router-ospf>
          </router>
          <interface>
          {loopback_config}
          {''.join(leaf_interface_snippet)}
          </interface>
        </native>
      </config>
    """

    result = task.run(netconf_edit_config, config=full_config_payload, target="running")



def main():
    nr = InitNornir(config_file="config.yml")

    nr_spines = nr.filter(F(groups__contains="spine"))
    nr_s8 = nr.filter(hostname="10.20.0.8")

    results = nr_s8.run(
        task=set_p2p_links,
        num_leafs=num_leafs
    )

    # Display the results
    print_result(results)

if __name__ == "__main__":
    main()

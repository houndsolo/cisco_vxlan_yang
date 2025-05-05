#!/usr/bin/env python3
from inventory.vars import *
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit
from nornir_utils.plugins.functions import print_result


# Define the number of spines. This could also come from Nornir inventory.
NUM_SPINES = 2

def set_p2p_links(task, num_spines):
    """
    Configures point-to-point links on leaf switches connecting to spines.
    Assumes interfaces are TenGigabitEthernet1/0/1, 1/0/2, etc.,
    corresponding to Spine 1, Spine 2, etc.
    Assigns unique IP addresses based on leaf node_id and spine index.
    """
    leaf_node_id = task.host["node_id"]
    config_fragments = [] # List to hold XML config for each interface

    for spine_index in range(num_spines):
        interface_port = spine_index + 1
        leaf_p2p_ip = f"10.240.{leaf_node_id}{spine_index+1}.1"
        leaf_loopback_ip = f"10.240.254.{leaf_node_id}"
        leaf_loopback_ip2 = f"10.240.250.{leaf_node_id}"
        p2p_ip_mask = "255.255.255.254"

        # Construct XML payload fragment for this specific interface
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
         <description>ibgp peering</description>
         <ip>
           <address>
             <primary>
               <address>{leaf_loopback_ip}</address>
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
               <address>{leaf_loopback_ip2}</address>
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
                  <router-id>10.240.254.{leaf_node_id}</router-id>
                </process-id>
              </ospf>
            </router-ospf>
          </router>
          <interface>
          {loopback_config}
          {''.join(config_fragments)}
          </interface>
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
    nr_leafs = nr.filter(F(groups__contains="leaf"))

    # Define the number of spines (can be made dynamic via inventory/config)

    # Run the task on the filtered leaf devices, passing the number of spines
    results = nr_leafs.run(
        task=set_p2p_links,
        num_spines=num_spines
    )

    # Display the results
    print_result(results)

if __name__ == "__main__":
    main()

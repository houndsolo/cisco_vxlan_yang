#!/usr/bin/env python3
from inventory.vars import *
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netconf.plugins.tasks import netconf_edit_config, netconf_lock, netconf_commit
from nornir_utils.plugins.functions import print_result


def system_config_payload(task):
    """set system settings"""
    switch_id = task.host["switch_id"]
    config_payload = f"""
      <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
          <spanning-tree>
            <extend xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree">
              <system-id/>
            </extend>
            <mst xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree">
              <instance-range>
                <id>0</id>
                <priority-root>
                  <priority>61440</priority>
                </priority-root>
                <priority>61440</priority>
              </instance-range>
            </mst>
            <mode xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-spanning-tree">mst</mode>
          </spanning-tree>
          <vtp>
            <mode xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-vtp">
              <transparent/>
            </mode>
          </vtp>
          <system>
            <mtu xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-switch">
              <size>9169</size>
            </mtu>
          </system>
          <errdisable>
            <detect>
              <cause-config>
                <gbic-invalid>false</gbic-invalid>
              </cause-config>
            </detect>
          </errdisable>
          <hostname>{task.host.name}</hostname>
            <interface>
              <Vlan>
                <name>{monitoring_vlan}</name>
                <ip>
                  <address>
                    <primary>
                      <address>10.{monitoring_vlan}.0.{switch_id}</address>
                      <mask>255.255.0.0</mask>
                    </primary>
                  </address>
                </ip>
              </Vlan>
            </interface>
          <banner>
            <login>
              <banner xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="replace">
            {task.host.name}.lylat.space
              </banner>
            </login>
          </banner>
          <snmp-server>
            <community-config xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-snmp">
              <name>pubic</name>
              <permission>ro</permission>
            </community-config>
            <contact xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-snmp">the Architect</contact>
            <location xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-snmp">home</location>
          </snmp-server>
        </native>
      </config>
    """

    result = task.run(netconf_edit_config, config=config_payload, target="running")

def main():
    # Initialize Nornir with your config.yaml pointing at inventory/*
    nr = InitNornir(config_file="config.yml")
    nr_spines = nr.filter(groups__contains="spine")
    nr_leafs = nr.filter(F(groups__contains="leaf"))
    nr_s10 = nr.filter(hostname="10.20.0.10")

    # Run the NETCONF 'get-capabilities' RPC on all hosts
    results = nr_leafs.run(task=system_config_payload)

    # Display which devices successfully connected and their capabilities
    print_result(results)

if __name__ == "__main__":
    main()

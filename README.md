
# Cisco VXLAN YANG Automation

This repository automates VXLAN configuration on Cisco Catalyst 9300 switches using Python and Nornir/NETCONF/YANG.
Topology: Two Cisco 9300 spines and Two 9300 leaves.

Additionally, 7 virtualized vxlan leaves, one on each of my hypervisors.

## Overview

The project generates and applies VXLAN configurations to spine and leaf switches via NETCONF.

## Inventory

Cisco 9300s are defined in `inventory/hosts.yml` with attributes:
- switch_id - unique ID for management
- node_id - unique per device class (spine/leaf/remote), for IP/interface numbering

Virtual VyOS Leaves are defined in `inventory/vars.py` `vyos_leafs` with attributes:
- hostname
- host_node
- node_id
- spine_connections
  - spine_id, interface - explicitly define which port each hypervisor is connected to


## Scripts

- `main.py` – Orchestrates configuration deployment.
- `set_banner.py` – Sets system-wide configuration.
- `set_bgp_leaf.py` – Configures BGP and EVPN on leaf switches.
- `set_bgp_spine.py` – Configures BGP on spine switches.
- `set_p2p_links_leaf.py` – Configures point-to-point links on leaf switches.
- `set_p2p_links_spine.py` – Configures point-to-point links on spine switches.

## Requirements

- `ncclient`
- `lxml`
- `nornir`
- `nornir_ansible` - ansible style inventory
- Cisco IOS XE devices with NETCONF enabled

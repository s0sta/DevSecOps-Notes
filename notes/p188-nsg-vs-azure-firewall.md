---
id: p188
title: "NSG vs Azure Firewall"
slug: nsg-vs-azure-firewall
sections: [devsecops]
topic: "DevSecOps & cloud security"
tags: [Azure, AZ104, NetworkSecurity, CloudComputing, CyberSecurity]
source: "LinkedIn post P188 · Cloud / DevSecOps series"
linkedin_date: 2027-12-09
design: compare
---

# NSG vs Azure Firewall

Azure gives you two very different tools for controlling network traffic, and AZ-104 expects you to know when each applies. They are not either/or; most real designs use both.

## Quick reference

| | **NSG** | **AZ FIREWALL** |
|:--|:--|:--|
| Layer | 3-4 (IP, port) | 3-7 (incl. FQDN) |
| Scope | Subnet or NIC | Whole virtual network |
| Cost | Free | Paid, per hour + data |
| Filter by domain | No | Yes (FQDN rules) |
| Threat intel | No | Yes |
| Best for | Basic segmentation | Central egress control |

**NSG** (Network Security Group): Free, basic allow/deny rules attached to subnets and NICs.

Example: `allow 443 from 10.0.0.0/16`

**AZ FIREWALL** (Managed firewall service): A paid, managed firewall for the whole network, with more features.

Example: `allow *.windowsupdate.com`

- NSG → free, basic rules on every subnet. Always use them.
- Azure Firewall → central, advanced control when you need it.

## Explained

A Network Security Group (NSG) is a set of basic allow and deny rules, evaluated by priority, that you attach to a subnet or a network interface. It filters by source and destination IP, port and protocol, which is layers 3 and 4. It is free, built in, and the right way to do basic segmentation: let the web subnet reach the database subnet on 5432, and nothing else. There is no reason not to use NSGs everywhere.

Azure Firewall is a managed, stateful firewall service for an entire virtual network. It does everything an NSG does and more: filtering by fully qualified domain name (allow traffic to \*.windowsupdate.com but not the wider internet), threat intelligence feeds, and central logging. It is a paid service, billed per hour plus data processed, and it usually sits at the edge of a hub network to control all outbound traffic.

### How to choose

NSGs for basic, free, per-subnet rules. Use them as the baseline on every network.  
Azure Firewall when you need central control, especially outbound: filtering which domains your VMs may reach, applying threat intelligence, and logging everything in one place.

The common pattern: NSGs on every subnet for segmentation, and an Azure Firewall in a hub for centralised egress filtering. The NSG is your fence between rooms; the firewall is the guarded main gate.

For the exam, remember: NSG is L3-L4 and free; Firewall adds FQDN filtering and threat intel for a cost.

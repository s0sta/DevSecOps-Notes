---
id: p493
title: "The VPC troubleshooting cheat sheet"
slug: the-vpc-troubleshooting-cheat-sheet
sections: [devsecops]
topic: "Cloud: AWS & Azure"
tags: [AWS, VPC, Troubleshooting, Networking, DevOps]
source: "LinkedIn post P493 · Network series"
linkedin_date: 2029-11-20
design: cheatsheet
---

# The VPC troubleshooting cheat sheet

The console is green, the health check is green, and the packet still dies. The VPC does not have one place to look; it has four.

## Quick reference

### Addresses

```bash
aws ec2 describe-vpcs --output table
aws ec2 describe-subnets --output table
aws ec2 describe-addresses
ip -br addr
ip route get 10.0.1.7
```

### Routes

```bash
aws ec2 describe-route-tables
aws ec2 describe-route-tables | jq .
ip route show table main
ip route get 8.8.8.8
ip route
```

### Firewall

```bash
aws ec2 describe-security-groups
aws ec2 describe-security-group-rules
aws ec2 describe-network-acls
aws ec2 describe-network-acl-entries
aws ec2 describe-vpc-endpoints
```

### Flow logs

```bash
aws ec2 describe-flow-logs
aws logs describe-log-groups
aws logs tail /aws/vpc/flowlogs
aws logs tail /aws/vpc/flowlogs --follow
aws s3 ls s3://my-flow-logs/
```

## Explained

### Addresses

Start with what exists. `aws ec2 describe-vpcs --output table` and `aws ec2 describe-subnets --output table` show the CIDR plan and the subnets. `aws ec2 describe-addresses` shows the Elastic IPs, and `ip -br addr` plus `ip route get 10.0.1.7` on the instance show what it believes.

### Routes

`aws ec2 describe-route-tables` prints the routes and their state. Read the local route, then the default route, then the association. A subnet with no explicit association uses the main table, which is a common surprise. `ip route show table main` and `ip route get 8.8.8.8` confirm the instance side, and `ip route` is the short view.

### Firewall

`aws ec2 describe-security-groups`, `aws ec2 describe-security-group-rules` and `aws ec2 describe-network-acls` list the rules. Remember the direction: security groups are stateful, NACLs are not. `aws ec2 describe-vpc-endpoints` answers the other half: whether the traffic was meant to stay inside AWS.

### Flow logs

`aws ec2 describe-flow-logs` says whether anyone is recording. `aws logs describe-log-groups` and `aws logs tail /aws/vpc/flowlogs --follow` read it back. If the logs go to S3, `aws s3 ls s3://my-flow-logs/` is the first command. A REJECT line turns a guess into a fact.

> **The honest caveat:** a command that returns nothing is not proof of health. It may be the wrong Region, the wrong profile or the wrong account.

> **The lesson:** check the layer the packet is on, not the layer the console draws.

## In one line

> **Find the hop that says no.** A green console is a claim, not a proof.

**Check a subnet**

```bash
aws ec2 describe-subnets
```

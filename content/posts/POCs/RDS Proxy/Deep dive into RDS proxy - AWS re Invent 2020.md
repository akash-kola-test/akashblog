---
title: Deep dive into RDS proxy - AWS re Invent 2020
date: 2025-01-07
draft: false
tags:
    - aws
    - rds
    - rds-proxy
---

## Introduction

Here are the today's application needs in terms of RDS (or) database

### Scalability

- Scale to hundreds of thousands of connections

![Deep dive into RDS proxy - AWS re Invent 2020 - Scalability](images/Deep%20dive%20into%20RDS%20proxy%20-%20AWS%20re%20Invent%202020%20-%20Scalability.png)

### Availability

- Increase app availability by reducing DB failover times
- no need to maintain application logic for handling failovers

![Deep dive into RDS proxy - AWS re Invent 2020 - Availability](images/Deep%20dive%20into%20RDS%20proxy%20-%20AWS%20re%20Invent%202020%20-%20Availability.png)

### Security

- Manage app data security with DB access controls

![Deep dive into RDS proxy - AWS re Invent 2020 - Security](images/Deep%20dive%20into%20RDS%20proxy%20-%20AWS%20re%20Invent%202020%20-%20Security.png)

### Possible solutions

- Overprovisioning
    - Database compute resources just for managing connections
    - Maintain complex failure handling code to overcome transient failures
- Self-managing a database proxy
    - Deploy, patch, and manage yet another component
    - Distribute across AZs for high availability

### Solution

Amazon RDS Proxy is the AWS service to help us in this solution.

## Amazon RDS Proxy

- A fully managed service

    - No need of deploying, patching, and managing needed

- Highly available database proxy for Amazon RDS and Amazon Aurora

    - AWS take cares of availability of the proxy incase of any AZ failures.

- Scalable

    - RDS proxy pools and shared DB connections to make applications more scalable.

- Database failures

    - Keeps the connections and transactions in queue with in proxy when database in failover time.

- More secure
    - Stores passwords in secrets manager
    - enforces IAM authentication

### Scalability

- Shares database connections between transactions with multiplexing.
- This scales to support hundreds of thousands of connections and this depends on size of the database.

> [!important]
> Based on instance size we can configure the max connections I guess

![Deep dive into RDS proxy - AWS re Invent 2020 - Connection pooling](images/Deep%20dive%20into%20RDS%20proxy%20-%20AWS%20re%20Invent%202020%20-%20Connection%20pooling.png)

#### Demo

#### Testing or Visual Proofs

### Seamless and fast failovers

- Applications connections are preserved and transactions are queued during failovers.
- Detects failovers and connects to standby quicker, bypassing DNS caches and downstream TTLs.
- Basically proxy directly connects with the DB instance instead of using the endpoint powered to detect the correct DB instance endpoint. This gives the ability to quickly move towards standby from master when there is a failover for master.

![Deep dive into RDS proxy - AWS re Invent 2020 - Failover](images/Deep%20dive%20into%20RDS%20proxy%20-%20AWS%20re%20Invent%202020%20-%20Failover.png)

#### Demo

#### Testing or Visual Proofs

### Security

RDS Proxy supports two types of authentication

- typical username and password authentication
- enforced IAM authentication

#### Typical username and password authentication

RDS will store the username and password under its secret manager. Whenever we try to authenticate with RDS Proxy it will try to match those credentials with stored credentials in its secret manager.

#### Enforced IAM Authentication

RDS Proxy also supports IAM authentication, where we will supply the generated token as password for RDS Proxy. The token can be generated from RDS using an API call. With this IAM authentication in place, the database passwords will never reach to the code.

![Deep dive into RDS proxy - AWS re Invent 2020 - IAM Authentication](images/Deep%20dive%20into%20RDS%20proxy%20-%20AWS%20re%20Invent%202020%20-%20IAM%20Authentication.png)

#### Demo

## Pricing model

- There are no additional charges associated with the default endpoint you get when you create an Amazon RDS Proxy.
- Adding an Amazon RDS Proxy endpoint provisions an AWS PrivateLink interface endpoint, which incurs additional charges as described on the [PrivateLink pricing page](https://aws.amazon.com/privatelink/pricing/).
- Amazon RDS Proxy is **priced based on the capacity of underlying instances**. For provisioned instances on Amazon Aurora, Amazon Relational Database Service (Amazon RDS) for MariaDB, Amazon Relational Database Service (Amazon RDS) for MySQL, and Amazon Relational Database Service (Amazon RDS) for PostgreSQL, Amazon RDS **Proxy is priced per vCPU per hour**.
- Partial hours are billed in 1-second increments with a 10-minute minimum charge following a billable status change such as creating, starting, or modifying.

![Deep dive into RDS proxy - AWS re Invent 2020 - Cost pricing us-east-2](images/Deep%20dive%20into%20RDS%20proxy%20-%20AWS%20re%20Invent%202020%20-%20Cost%20pricing%20us-east-2.png)

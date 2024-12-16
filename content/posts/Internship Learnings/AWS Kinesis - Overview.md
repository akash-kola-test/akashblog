---
title: AWS Kinesis - Overview
date: 2024-12-16
draft: 
tags:
  - aws
  - kinesis
---


We can use Amazon Kinesis Data Streams to collect and process large streams of data records in real time

![AWS Kinesis - High Level Architecture](images/AWS%20Kinesis%20-%20High%20Level%20Architecture.png)


A Kinesis stream is made of set of shards. Each shard has a sequence of records. Each data record has a sequence number assigned to it

Data Record is nothing but a unit of data which might indicate some event or just a message

### Capacity Mode
We you can choose between an **on-demand** mode and a **provisioned** mode for data streams. With on-demand mode, Kinesis will automatically manages the shards in order to provide necessary throughput. But with provisioned mode we must specify the number of shards for the data stream. 

The total capacity of a data stream is the sum of the capacities of its shards. We can increase or decrease the number of shards in a data stream as needed and we are charged for the number of shards at an hourly rate.

### Retention Period
The _retention period_ is the length of time that data records are accessible after they are added to the stream. A stream’s retention period is set to a default of 24 hours after creation. We can increase the retention period up to 8760 hours (365 days)

### Shard
A _shard_ is a uniquely identified sequence of data records in a stream. A stream is composed of one or more shards, each of which provides a fixed unit of capacity. Each shard can support up to 5 transactions per second for reads, up to a maximum total data read rate of 2 MB per second and up to 1,000 records per second for writes, up to a maximum total data write rate of 1 MB per second (including partition keys). The data capacity of your stream is a function of the number of shards that you specify for the stream. The total capacity of the stream is the sum of the capacities of its shards.

### Partition Key
A _partition key_ is used to group data by shard within a stream. Kinesis Data Streams segregates the data records belonging to a stream into multiple shards. It uses the partition key that is associated with each data record to determine which shard a given data record belongs to.


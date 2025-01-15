---
title: InfluxDB Storage Engine
date: 2024-11-29
draft: false
tags:
  - influxdb
---
## Shards

Basically data is organized into shards of time, each is an underlying DB which makes it efficient to drop old data

![Shards](images/Shards.png)

## Organizing data in a key value store

Basically each series and field maps to a unique ID as seen in the below picture

![Series and fields](images/Series%20and%20fields.png)

We can arrange the data with key as ID and time, and the value being the field value and the key is always sorted

![Ordered Key Space Example](images/Ordered%20Key%20Space%20Example.png)

Many storage engines have this model for example [Level DB](https://github.com/google/leveldb), [LMDB](https://en.wikipedia.org/wiki/Lightning_Memory-Mapped_Database), and other key values stores. But still they won't give all necessary features needed for time series data.

## Issues with Level DB

For implementing InfluxDB storage engine, Level DB has following issues

- deletes are expensive
- too many open file handles

## Issues with LMDB Implementation

For implementing InfluxDB storage engine, LM DB implementations has following issues

- write throughput
- no compression

## InfluxDB's Storage Engine (Time Structured Merge tree - TSM)

It's almost similar to how LSM Trees works, also compression will happen based on data types. Here is typical write workflow that happens with incoming time series:

- write the incoming time series data to the WAL
- write that also to the in memory data structure and send the write successful response
- periodically in memory data flushes to the TSM files

![TSM Components](images/TSM%20Components.png)

## InfluxDB's Storage Engine (Inverted Index)

Here is the sample query which we need to execute on our storage engine

![Example Query](images/Example%20Query.png)

We will use the inverted index to map the incoming query as series search, like every series will have it's unique ID and we need maintain what fields does each measurement is having, also we need store what tag keys' having it as values, and the posting lists which will store the IDs that were under the specific measurements, tags values as specified in the picture. This way we will which IDs we needed from out data structure to query

![Inverted Index Idea](images/Inverted%20Index%20Idea.png)

This data will needs to in memory so that we can quickly know what IDs fall under a query, so for this again we will use the same LSM tree structure. And when booting up it will read the entire disk data structure and fill up the in memory index.

![Inverted Index Maintainance](images/Inverted%20Index%20Maintainance.png)
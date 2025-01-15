---
title: InfluxDB
date: 2024-11-29
draft: false
tags:
- influxdb
---
The open source time series platform designed to store, query, and process time series data. Also InfluxDB supports up to **nano seconds precision** for more advanced use cases.

## Time Series

Time series are simply measurements or events that are tracked, monitored, down sampled and aggregated over time. This could be server metrics, application performance monitoring, network data, sensor data, events, clicks, trades in a market and many other types of analytical data. *The key difference that separates time series data from regular data is that you’re always asking questions about it over time.*

![Time series with stocks](images/Time%20series%20with%20stocks.png)

Time series data comes in two forms: **regular** and **irregular**. Regular time series consist of measurements gathered from software or hardware sensors at regular intervals of time (every 10 seconds, for example) and are often referred to as metrics. Irregular time series are events driven either by users or other external events. Summarizations of irregular time series become regular themselves.

## Interacting with InfluxDB

- User Interface
- CLI
- SDKs
- API
- Tools like Telegraf

## Higher Level Data Model

Organization
	Bucket
		Record (Measurement, Tags, Field, Timestamp, Field Value)


## Line Protocol

The InfluxDB platform organizes time series in a structured format. At the top level is a measurement name, followed by a set of key/value pairs called tags that describe the metadata, followed by key/value pairs of the actual values called fields. Field values in InfluxDB can be boolean, int64, float64 or strings. Finally, there is a timestamp for the set of values. All data is queried by the measurement, tags, and field along with the time range.

- **measurement**: String that identifies the measurement to store the data in.
- **tag set**: Comma-delimited list of key value pairs, each representing a tag. Tag keys and values are unquoted strings. _Spaces, commas, and equal characters must be escaped._
- **field set**: Comma-delimited list key value pairs, each representing a field. Field keys are unquoted strings. _Spaces and commas must be escaped._ Field values can be strings (quoted), floats, integers, unsigned integers, or booleans.
- **timestamp**: [Unix timestamp](https://docs.influxdata.com/influxdb/v2/reference/syntax/line-protocol/#unix-timestamp) associated with the data. InfluxDB supports up to nanosecond precision. _If the precision of the timestamp is not in nanoseconds, you must specify the precision when writing the data to InfluxDB._

![Line Protocol syntax](images/Line%20Protocol%20syntax.png)
![Line Protocol Example](images/Line%20Protocol%20Example.png)

## Basic Terms

**Point:** A single data record is referred to as point or data point. For example,

	cpu,ec2_instance_name=ec2_1,region=NVirgina CPUUtilization=4.5 1733289889

**Series:** A single series which will have data over time. For example, the series **cpu,ec2_instance_name=ec2_1,region=Mumbai#CPUUtilization** having the time over data like the following

	(1733289889, 4.5)
	(1733289890, 5.5)
	(1733289891, 5.2)


## Main features of InfluxDB

- Collect Data
- Explore the data
- Create dashboards out of the data
- Schedule tasks for automations
- Maintain alerts for notification

## ## InfluxDB ecosystem

The InfluxData open source time series platform consists of two main components: InfluxDB and Telegraf. These tools work together to make it easy to collect, store, and analyze your time series data.

### Telegraf 

Telegraf is the data collection component in the InfluxData ecosystem, designed to gather metrics from a variety of sources and write them into InfluxDB. It's a plugin-driven server agent that can collect data from a wide array of sources and communication protocols

### InfluxDB 

InfluxDB serves as the core database responsible for storing and analyzing time series data in the InfluxData ecosystem. It is designed to handle **high-velocity** and **high-volume** data streams with **low latency**, making it especially well-suited for applications that require real-time analytics.

## Time series data storage capabilities

These are main capabilities that needed to be supported by Time series based data storage engine

- high write throughput
- awesome read performance
- better compression
- reads can't block writes
- writes can't block reads


## References
- [InfluxDB Practical Basic Examples]({{< ref "InfluxDB Practical Basic Examples.md" >}})
- High level internal details about [InfluxDB Storage Engine]({{< ref "InfluxDB Storage Engine.md" >}})

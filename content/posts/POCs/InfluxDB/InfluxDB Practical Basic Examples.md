---
title: InfluxDB Practical Basic Examples
date: 2024-11-29
draft: 
tags:
  - influxdb
---
# Contents

- [Setup](#setup)
- [Writing Data](#writing-data)
- [Query](#query)

## Setup

1. Run the docker container for InfluxDB using docker compose

```yml
  influxdb2:
    image: influxdb:2.7.11-alpine
    container_name: influxdb
    ports:
      - 8086:8086
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: akashnani
      DOCKER_INFLUXDB_INIT_PASSWORD: Akashnani@123#
      DOCKER_INFLUXDB_INIT_ORG: akashorg
      DOCKER_INFLUXDB_INIT_BUCKET: sensor_data
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: "my-super-secret-auth-token"
    volumes:
      - type: volume
        source: influxdb2-data
        target: /var/lib/influxdb2
      - type: volume
        source: influxdb2-config
        target: /etc/influxdb2
    networks:
      influxdb:
```

![InfluxDB docker compose up command](images/InfluxDB%20docker%20compose%20up%20command.png)

2. Open the localhost:8086 and login with the user details

3. Create a sample bucket for our practical

![Create Bucket](images/Create%20Bucket.png)

## Writing Data

1. Click on Write data and select line protocol

![Write Data options](images/Write%20Data%20options.png)

2. Select the sample bucket and enter the following data

```line-protocol
home,room=Living\ Room temp=21.1,hum=35.9,co=0i 1641024000
home,room=Kitchen temp=21.0,hum=35.9,co=0i 1641024000
home,room=Living\ Room temp=21.4,hum=35.9,co=0i 1641027600
home,room=Kitchen temp=23.0,hum=36.2,co=0i 1641027600
home,room=Living\ Room temp=21.8,hum=36.0,co=0i 1641031200
home,room=Kitchen temp=22.7,hum=36.1,co=0i 1641031200
home,room=Living\ Room temp=22.2,hum=36.0,co=0i 1641034800
home,room=Kitchen temp=22.4,hum=36.0,co=0i 1641034800
home,room=Living\ Room temp=22.2,hum=35.9,co=0i 1641038400
home,room=Kitchen temp=22.5,hum=36.0,co=0i 1641038400
home,room=Living\ Room temp=22.4,hum=36.0,co=0i 1641042000
home,room=Kitchen temp=22.8,hum=36.5,co=1i 1641042000
home,room=Living\ Room temp=22.3,hum=36.1,co=0i 1641045600
home,room=Kitchen temp=22.8,hum=36.3,co=1i 1641045600
home,room=Living\ Room temp=22.3,hum=36.1,co=1i 1641049200
home,room=Kitchen temp=22.7,hum=36.2,co=3i 1641049200
home,room=Living\ Room temp=22.4,hum=36.0,co=4i 1641052800
home,room=Kitchen temp=22.4,hum=36.0,co=7i 1641052800
home,room=Living\ Room temp=22.6,hum=35.9,co=5i 1641056400
home,room=Kitchen temp=22.7,hum=36.0,co=9i 1641056400
home,room=Living\ Room temp=22.8,hum=36.2,co=9i 1641060000
home,room=Kitchen temp=23.3,hum=36.9,co=18i 1641060000
home,room=Living\ Room temp=22.5,hum=36.3,co=14i 1641063600
home,room=Kitchen temp=23.1,hum=36.6,co=22i 1641063600
home,room=Living\ Room temp=22.2,hum=36.4,co=17i 1641067200
home,room=Kitchen temp=22.7,hum=36.5,co=26i 1641067200
```

![Write Data](images/Write%20Data.png)

## Query

We can write queries to get the information needed for us, just click on Data explorer, write the query and submit

```flux
from(bucket: "sensor_data")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "home")
  |> filter(fn: (r) => r["_field"] == "temperature")
  |> filter(fn: (r) => r["room"] == "kitchen")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")
```

![Query Output](images/Query%20Output.png)
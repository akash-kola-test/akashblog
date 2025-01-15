---
title: Hard disk partitions
date: 2025-01-15
draft: 
tags:
  - "#linux"
  - "#harddisk"
---


Every hard disk is just a device in Linux. If we want to use the partition we need to create partitions in it.

## Sectors

Hard disk can't understand GBs, MBs, etc.. it can only understand the storage in terms of **sectors**. A **sector is 512 bytes**, so typically 100 GiB hard disk means 107,374,182,400 bytes and 209,715,200 sectors.

>[!info]
>We can use **fdisk** command to get information or perform some operations on disks.

```sh
fdisk -l # to get information about disks

fdisk -l /dev/sdb # to get information about /dev/sdb disk

fdisk # to perform operations on disks

lsblk # to get information about blocks (storage, hard disk)
```

## Partition Types

### Primary Partition

For any disk, we can create **only 4 partitions** which we call them as primary partitions. The reason behind why we can only create only 4 partitions is partition table size constraint.

### Partition Table

Partition table is a table which will store information about partitions. To store single partition information this partition table needs 16 bytes, and total **size of partition table is 64 bytes** which in turn put the constraint of able to create only 4 partitions totally. This is because we can't store more than 4 partitions info in table.

### Extended Partition

To solve the issue of only 4 partitions, extended partition will help. **Extended partition will be treated as new hard disk** by the OS. Because of this, we can more than 4 partitions inside the new extended partition and they are called **logical partitions**.


## Creating and Using partition 

To create partition we should follow the below three steps

1. Create partition
2. Format the partition
3. Mount the partition

>[!important]
>To settle down the created partitions we need to use either *udevadm settle* or *partprobe deviceName*  in RedHat linux


## Format

To use the partition, first we need to format so that it can create an **inode** table which can be used to store files' details.

To format a partition we can use the following command:

```sh
mkfs.ext4 /dev/sdb1 # ext4 is an format type
```


## Mount

To use the partition or hard disk we need to mount it to a folder.

```sh
mount /dev/sdb1 /mountpoint-folder # device name and mount point
```


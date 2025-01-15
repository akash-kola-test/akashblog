---
title: Network Attach Storage (NAS)
date: 2025-01-15
draft: 
tags:
  - "#linux"
  - "#nas"
  - "#nfs"
---
Network attached storage is just an storage that will be available from network to store the data. This makes out file storage to be centralized and eliminates the local presence for using the storage as it available over network.

## NFS

NFS is a protocol to use the network attached storage.

## Server installation and setup

1. First we need to install the NFS server package, following command can be used in RedHat Linux

```sh
yum install -y nft-utils
```

2. Create sharing folder

```sh
mkdir /sharing-folder
```

3. configure /etc/exports file

```txt
/sharing-folder 192.168.17.1(rw,root_squash)
```

4. Restart the NFS server

```sh
systemctl restart nfs-server
```


## Mounting folder client side

To mount the server shared folder, we just need to run the mount command 

```sh
mount 192.168.17.2:/sharing-folder /mount-point-folder # 192.168.17.2 is server IP
```


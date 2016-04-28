#!/bin/bash

#Setup Up Redis
sudo apt-get update -y
sudo apt-get install redis-server -y

#See http://redis.io/topics/admin
sudo sysctl vm.overcommit_memory=1

sudo sh -c "echo never > /sys/kernel/mm/transparent_hugepage/enabled"

#TODO Set Swap to memory size

#Set maxmemory correctly

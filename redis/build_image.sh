#!/bin/bash

#Packer docs recommend sleeping first
sleep 30

#Setup Up Redis
sudo apt-get update -y
sudo apt-get install redis-server -y

#See http://redis.io/topics/admin
#sudo sysctl vm.overcommit_memory=1

#sudo sh -c "echo never > /sys/kernel/mm/transparent_hugepage/enabled"

#TODO Set Swap to memory size

#Set maxmemory correctly

sudo sed -i -e 's/bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis/redis.conf
sudo sed -i -e 's/# cluster-enabled yes/cluster-enabled yes/g' /etc/redis/redis.conf
sudo sed -i -e 's/# cluster-config-file nodes-6379.conf/cluster-config-file nodes-6379.conf/g' /etc/redis/redis.conf
sudo sed -i -e 's/# cluster-node-timeout 15000/cluster-node-timeout 15000/g' /etc/redis/redis.conf
sudo sed -i -e 's/# cluster-slave-validity-factor 10/cluster-slave-validity-factor 10/g' /etc/redis/redis.conf
sudo sed -i -e 's/# cluster-migration-barrier 1/cluster-migration-barrier 1/g' redis.conf
sudo sed -i -e 's/# cluster-require-full-coverage yes/cluster-require-full-coverage no/g' /etc/redis/redis.conf

sudo service redis-server restart


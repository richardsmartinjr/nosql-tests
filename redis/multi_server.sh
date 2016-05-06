#!/bin/bash

for (( i=0; i < 9; i++ ))
do

vm_names=( "redis-master1" "redis-master2" "redis-master3" "redis-slave1" "redis-slave2" "redis-slave3" "redis-slave4" "redis-slave5" "redis-slave6")
vm_zones=( "us-central1-f" "us-central1-a" "us-central1-b" "us-central1-c" "us-central1-f" "us-central1-a" "us-central1-b" "us-central1-c" "us-central1-f")


gcloud compute --project "cdpipeline-1212" instances create "${vm_names[i]}" \
 --zone "${vm_zones[i]}" --machine-type "n1-standard-1" \
 --network "default" --maintenance-policy "MIGRATE" \
 --scopes default="https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring.write","https://www.googleapis.com/auth/cloud.useraccounts.readonly" \
 --image "/cdpipeline-1212/redis-server-ubuntu16-05052016" \
 --boot-disk-size "10" --boot-disk-type "pd-ssd" \
 --boot-disk-device-name "${vm_names[i]}" \
 --quiet

done 

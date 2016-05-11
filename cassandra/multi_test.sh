#!/bin/bash


export NAME=$(hostname)'-thread-0'
python3 test.py -n $NAME > 0.out &

sleep 10
for (( i=1; i < 40; i++ ))
do

export NAME=$(hostname)'-thread-'$i


python3 test.py -n $NAME > $i.out &

done

#/bin/bash

log_file=$1
out_file=$2

> $out_file

while true
do
    while IFS='' read -r line || [[ -n "$line" ]]
    do
        echo $line >> $out_file
        sleep 0.5
    done < $log_file
done
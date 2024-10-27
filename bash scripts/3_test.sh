#!/bin/bash
fio_file="Exo3_2"
output_dir="./fio_results_$fio_file"
data_dir="./data_$fio_file"
mkdir -p ${output_dir}
mkdir -p ${data_dir}

# Define default parameters
runtime=60
numjobs=1
filesize=1G
direct=1
repetitions=5
rw=write

echo "Running random tasks with bssplit"
for rep in $(seq 1 $repetitions)
do
  fio --name=${fio_file}_bssplit_rep_${rep} \
      --runtime=$runtime \
      --numjobs=$numjobs \
      --bssplit=64k:100 \
      --filesize=$filesize \
      --direct=$direct \
      --rw=$rw \
      --output=${output_dir}/${fio_file}_bssplit_rep_${rep}_output.json --output-format=json
  
  echo "Completed random task with bssplit, repetition: $rep"
  mv ${fio_file}_bssplit_rep_${rep}.* ${data_dir}/
done

echo "All tasks completed."

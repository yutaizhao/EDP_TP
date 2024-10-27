#!/bin/bash
fio_file="Exo4"
output_dir="./fio_results_$fio_file"
data_dir="./data_$fio_file"
mkdir -p ${output_dir}
mkdir -p ${data_dir}

# Define fixed parameters

runtime=60
blocksize=16k
filesize=1G
direct=1
rwmixwrite=30
rw=randrw
repetitions=5

# Tâches avec 1, 2, 4, 6 et 8 processus tournant en parallèle.
echo "Running tasks with varying parallel jobs (1, 2, 4, 6, 8)..."
for numjobs in 1 2 4 6 8
do
  for rep in $(seq 1 $repetitions)  # 每个任务重复5次
  do
    fio --name=${fio_file}_parallel_${numjobs}_rep_${rep} \
        --runtime=$runtime \
        --rw=$rw \
        --rwmixwrite=$rwmixwrite \
        --bs=$blocksize \
        --filesize=$filesize \
        --direct=$direct \
        --numjobs=$numjobs \
        --output=${output_dir}/${fio_file}_parallel_${numjobs}_rep_${rep}_output.json --output-format=json
    
    echo "Completed task with ${numjobs} parallel jobs, repetition: $rep"
    mv ${fio_file}_parallel_${numjobs}_rep_${rep}.* ${data_dir}/
  done
done

echo "All tasks completed."


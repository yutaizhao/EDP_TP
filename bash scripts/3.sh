#!/bin/bash
fio_file="Exo3"
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

#Tâche de requêtes en écriture avec 30% de requêtes de 4Ko, 60% de 16Ko et 10% de 64Ko (bssplit).
echo "Running random tasks with bssplit (30% 4KB, 60% 16KB, 10% 64KB)..."
for rep in $(seq 1 $repetitions)
do
  fio --name=${fio_file}_bssplit_rep_${rep} \
      --runtime=$runtime \
      --numjobs=$numjobs \
      --bssplit=4k:30,16k:60,64k:10 \
      --filesize=$filesize \
      --direct=$direct \
      --rw=$rw \
      --output=${output_dir}/${fio_file}_bssplit_rep_${rep}_output.json --output-format=json
  
  echo "Completed random task with bssplit, repetition: $rep"
  mv ${fio_file}_bssplit_rep_${rep}.* ${data_dir}/
done

echo "All tasks completed."

#!/bin/bash
fio_file="Exo1"
output_dir="./fio_results_$fio_file"
data_dir="./data_$fio_file"
mkdir -p ${output_dir}
mkdir -p ${data_dir}

# Define default parameters
runtime=60
numjobs=1
blocksize=16k
filesize=1G
direct=1
repetitions=5 

#Tâches avec un pourcentage d’écriture variant de 0 à 100% par pas de 12.5 pour des accès aux données séquentiels, puis aléatoires.

# Run sequential
echo "Running sequential tasks with varying write percentages..."
for write_percentage in $(seq 0 12.5 100)
do
  for rep in $(seq 1 $repetitions)
  do
    fio --name=${fio_file}_seq_${write_percentage}_rep_${rep} \
        --runtime=$runtime \
        --numjobs=$numjobs \
        --rwmixwrite=$write_percentage \
        --bs=$blocksize \
        --filesize=$filesize \
        --direct=$direct \
        --rw=rw \
        --output=${output_dir}/${fio_file}_seq_${write_percentage}_rep_${rep}_output.json --output-format=json
    
    echo "Completed sequential task with write percentage: $write_percentage%, repetition: $rep"
    mv ${fio_file}_seq_${write_percentage}_rep_${rep}.* ${data_dir}/
  done
done

# Run random
echo "Running random tasks with varying write percentages..."
for write_percentage in $(seq 0 12.5 100)
do
  for rep in $(seq 1 $repetitions) 
  do
    fio --name=${fio_file}_rand_${write_percentage}_rep_${rep} \
        --runtime=$runtime \
        --numjobs=$numjobs \
        --rwmixwrite=$write_percentage \
        --bs=$blocksize \
        --filesize=$filesize \
        --direct=$direct \
        --rw=randrw \
        --output=${output_dir}/${fio_file}_rand_${write_percentage}_rep_${rep}_output.json --output-format=json
    
    echo "Completed random task with write percentage: $write_percentage%, repetition: $rep"
    mv ${fio_file}_rand_${write_percentage}_rep_${rep}.* ${data_dir}/
  done
done

echo "All tasks completed."


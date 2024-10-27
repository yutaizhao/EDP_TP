#!/bin/bash
fio_file="Exo2"
output_dir="./fio_results_$fio_file"
data_dir="./data_$fio_file"
mkdir -p ${output_dir}
mkdir -p ${data_dir}

# Define default parameters
runtime=60
numjobs=1
filesize=1G
direct=1
rwmixwrite=33
repetitions=5
rw=randrw

#Tâches avec une taille de requête variant de 1ko à 1Mo par pas de puissance de 2.
echo "Running random tasks varying block sizes..."
for blocksize in 1k 2k 4k 8k 16k 32k 64k 128k 256k 512k 1m
do
  for rep in $(seq 1 $repetitions)
  do
    fio --name=${fio_file}_bs_${blocksize}_rep_${rep} \
        --runtime=$runtime \
        --numjobs=$numjobs \
        --rwmixwrite=$rwmixwrite \
        --filesize=$filesize \
        --direct=$direct \
        --rw=$rw\
        --bs=$blocksize \
        --output=${output_dir}/${fio_file}_bs_${blocksize}_rep_${rep}_output.json --output-format=json
    
    echo "Completed random task with blocksize: $blocksize, repetition: $rep"
    mv ${fio_file}_bs_${blocksize}_rep_${rep}.* ${data_dir}/
  done
done

echo "All tasks completed."


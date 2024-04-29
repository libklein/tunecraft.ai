#!/bin/bash

DYNAMIC_LIST=(meditation nature rain music ocean)

for i in "${DYNAMIC_LIST[@]}"; do
	# Make 100 requests
	for j in {101..1000}; do
		https --check-status "https://calmyleon.com/serve.php" "c==${i}" >"responses/${i}_${j}.json"
	done
done

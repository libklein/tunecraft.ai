#!/bin/bash

URL_PREFIX="https://cdn.calmyleon.com/Data/"

if [ $# -ne 2 ]; then
	echo "Usage: $0 <input-file> <output-dir>"
	exit 1
fi

INPUT_FILE=$1
OUTPUT_DIR=$2
# Loop over each line of the input file
while read -r url; do
	# Download the sound file
	output_file=${url#"$URL_PREFIX"}
	output_dir=$(dirname "$output_file")
	output_file_name=$(basename "$output_file")

	write_dir="${OUTPUT_DIR}/${output_dir}"
	mkdir -p "$write_dir"
	wget -q -O "${write_dir}/${output_dir}_${output_file_name}" "$url"
done <$INPUT_FILE

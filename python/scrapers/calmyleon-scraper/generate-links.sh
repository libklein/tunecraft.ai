#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Usage: $0 <output-file>"
	exit 1
fi

OUTPUT_FILE=$1

jq -r -s '.[] | "https://cdn.calmyleon.com/Data/" + .code + "/" + (.stem | tostring) + "a.ogg"' responses/* | sort | uniq >"$OUTPUT_FILE"
jq -r -s '.[] | "https://cdn.calmyleon.com/Data/" + .code + "/" + (.stem | tostring) + "b.ogg"' responses/* | sort | uniq >>"$OUTPUT_FILE"

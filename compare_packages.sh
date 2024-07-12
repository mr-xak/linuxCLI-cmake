#!/bin/bash

# This script runs the Python package comparator with the specified output format

# Check if the user has provided an output format
if [ -z "$1" ]; then
    echo "Please specify the output format (json or text):"
    read output_format
else
    output_format=$1
fi

# Validate the output format
if [[ "$output_format" != "json" && "$output_format" != "text" ]]; then
    echo "Invalid format. Please use 'json' or 'text'."
    exit 1
fi

# Run the Python script with the specified output format
python main.py --output $output_format

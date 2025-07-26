#!/bin/bash

PCAP_DIR="./pcap_database"
OUTPUT_DIR="./suricata_output"
SURICATA_CONFIG="/etc/suricata/suricata.yaml"

mkdir -p "$OUTPUT_DIR"

echo "File, Alerts, CPU(%), Memory(MB)" > suricata_metrics.csv

for pcap_file in "$PCAP_DIR"/*.pcapng; do
    filename=$(basename "$pcap_file")
    file_output_dir="$OUTPUT_DIR/${filename%.*}"
    mkdir -p "$file_output_dir"

    echo "Running Suricata on: $filename"

    # Run Suricata with time and collect CPU/MEM metrics
    /usr/bin/time -f "%P %M" -o "$file_output_dir/usage.txt" \
    sudo suricata -r "$pcap_file" -c "$SURICATA_CONFIG" -l "$file_output_dir"

    # Count number of alerts
    alert_file="$file_output_dir/fast.log"
    if [ -f "$alert_file" ]; then
        alert_count=$(wc -l < "$alert_file")
    else
        alert_count=0
    fi

    # Extract CPU and Memory usage from time output
    cpu_usage=$(awk '{print $1}' "$file_output_dir/usage.txt" | tr -d '%')
    mem_usage_kb=$(awk '{print $2}' "$file_output_dir/usage.txt")
    mem_usage_mb=$((mem_usage_kb / 1024))

    # Log metrics to CSV
    echo "$filename, $alert_count, $cpu_usage, $mem_usage_mb" >> suricata_metrics.csv

    echo "Finished: $filename → Alerts: $alert_count | CPU: $cpu_usage% | MEM: ${mem_usage_mb}MB"
    echo "--------------------------------------------"
done

echo "All PCAPs processed. Metrics saved in suricata_metrics.csv"

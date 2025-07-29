#!/bin/bash
 
PCAP="Downloads/Thursday-WorkingHours.pcap"
 
perf stat -e cycles,instructions,cache-references,cache-misses,context-switches,cpu-migrations,page-faults -o perf_output.txt &
 
PERF_PID=$!
 
/usr/bin/time -v suricata -r "$PCAP" 2>&1 | tee time_output.txt
 
kill $PERF_PID 2>/dev/null

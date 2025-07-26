#!/bin/bash

# Base URL
BASE_URL="https://www.malware-traffic-analysis.net/2025"

# List of dates to pull from
DATES=("07-23" "07-22" "07-21")  # You can add more manually or automate this part

# Create folder if not exists
mkdir -p pcap_database

for DATE in "${DATES[@]}"; do
    # Full page URL
    PAGE_URL="$BASE_URL/$DATE.html"

    echo ">>> Checking $PAGE_URL"

    # Get list of zip files
    ZIP_LINKS=$(wget -qO- "$PAGE_URL" | grep -oP '(?<=href=")[^"]+\.zip')

    for ZIP_PATH in $ZIP_LINKS; do
        ZIP_NAME=$(basename "$ZIP_PATH")
        FULL_URL="$BASE_URL/$ZIP_PATH"
        LOCAL_ZIP="pcap_database/$ZIP_NAME"
        
        echo ">>> Downloading $FULL_URL"
        wget --no-check-certificate -O "$LOCAL_ZIP" "$FULL_URL"

        # Derive password from date (format: infected_YYYYMMDD)
        ZIP_DATE=$(echo "$ZIP_NAME" | grep -oP '\d{8}')  # e.g., 20250723
        PASSWORD="infected_$ZIP_DATE"

        echo ">>> Unzipping $ZIP_NAME with password $PASSWORD"
        unzip -P "$PASSWORD" "$LOCAL_ZIP" -d pcap_database/
    done
done

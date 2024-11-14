#!/bin/bash

# Usage: ./ext_gen.sh START_NUMBER END_NUMBER

# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 START_NUMBER END_NUMBER"
    exit 1
fi

START_NUMBER_DEC="$1"
END_NUMBER_DEC="$2"

# Check if 'bc' and 'xxd' are installed
if ! command -v bc &> /dev/null; then
    echo "Error: 'bc' command not found. Please install bc to use this script."
    exit 1
fi

if ! command -v xxd &> /dev/null; then
    echo "Error: 'xxd' command not found. Please install xxd to use this script."
    exit 1
fi

# Convert decimal numbers to hexadecimal
START_NUMBER_HEX=$(printf '%x' "$START_NUMBER_DEC")
END_NUMBER_HEX=$(printf '%x' "$END_NUMBER_DEC")

# Ensure hexadecimal values have even length
if [ $(( ${#START_NUMBER_HEX} % 2 )) -ne 0 ]; then
    START_NUMBER_HEX="0$START_NUMBER_HEX"
fi

if [ $(( ${#END_NUMBER_HEX} % 2 )) -ne 0 ]; then
    END_NUMBER_HEX="0$END_NUMBER_HEX"
fi

# Convert hexadecimal values to binary and then to Base64
START_NUMBER_B64=$(echo "$START_NUMBER_HEX" | xxd -r -p | base64)
END_NUMBER_B64=$(echo "$END_NUMBER_HEX" | xxd -r -p | base64)

# Create the custom_ext.cnf file using ASN1:OCTETSTRING with Base64 encoding
cat > custom_ext.cnf <<EOL
[ extensions ]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

# Use Base64-encoded values with ASN1:OCTETSTRING
1.2.3.4.5.6.7.8.1 = ASN1:OCTETSTRING:${START_NUMBER_B64}
1.2.3.4.5.6.7.8.2 = ASN1:OCTETSTRING:${END_NUMBER_B64}
EOL

echo "custom_ext.cnf has been generated successfully with Base64-encoded 128-bit values."

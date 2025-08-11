#!/usr/bin/env python3
"""
This script detects the encoding of a file and converts it to UTF-8.
It is designed to fix file encoding issues that can prevent Python applications from starting.
"""

import sys
import os
import codecs

try:
    import chardet
except ImportError:
    print("Error: 'chardet' library not found. Please install it using: pip install charset-normalizer")
    sys.exit(1)

def fix_file_encoding(file_path, target_encoding='utf-8'):
    """
    Detects and fixes the encoding of a given file to the target encoding.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return

    # 1. Read file in binary mode
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
    except IOError as e:
        print(f"Error reading file: {e}")
        return

    if not raw_data:
        print(f"File '{file_path}' is empty. Nothing to do.")
        return

    # 2. Detect encoding
    result = chardet.detect(raw_data)
    detected_encoding = result['encoding']
    confidence = result['confidence']

    if not detected_encoding:
        print(f"Could not detect encoding for '{file_path}' with enough confidence. Manual check required.")
        return

    print(f"Detected encoding for '{file_path}': {detected_encoding} with {confidence:.2f} confidence.")

    # 3. Check if conversion is needed
    normalized_detected = detected_encoding.lower().replace('-', '_')
    normalized_target = target_encoding.lower().replace('-', '_')

    if normalized_detected == normalized_target and not raw_data.startswith(codecs.BOM_UTF8):
        print(f"File is already in the correct encoding ({target_encoding}). No changes needed.")
        return

    # 4. Convert the file
    try:
        # Handle BOM for UTF-8 files, otherwise decode with detected encoding
        if raw_data.startswith(codecs.BOM_UTF8):
            print("File has a UTF-8 BOM (Byte Order Mark).")
            # It's better to remove BOM from python source files for compatibility
            decoded_text = raw_data.decode('utf-8-sig')
            print("Removing UTF-8 BOM...")
        else:
            print(f"Converting from {detected_encoding} to {target_encoding}...")
            decoded_text = raw_data.decode(detected_encoding)

        # Re-encode with the target encoding (without BOM)
        new_data = decoded_text.encode(target_encoding)

        # 5. Write back to the file
        with open(file_path, 'wb') as f:
            f.write(new_data)

        print(f"Successfully converted and saved '{file_path}' as {target_encoding}.")

    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        print("The file was not modified.")

if __name__ == "__main__":
    # The check_encoding.py script points to this file as a potential issue.
    file_to_fix = "utils/legal_journey.py"
    
    # Construct full path relative to this script's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_file_path = os.path.join(base_dir, file_to_fix)

    print(f"--- Checking and fixing encoding for: {full_file_path} ---")
    fix_file_encoding(full_file_path)
    print("--- Finished ---")
    print("\nNow, try running your Flask application again:")
    print("python main.py")
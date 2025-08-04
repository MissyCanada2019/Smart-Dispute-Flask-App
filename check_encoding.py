import binascii
import chardet

def check_file_encoding(file_path):
    # Read file in binary mode
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    
    # Detect encoding
    result = chardet.detect(raw_data)
    
    # Print encoding information
    print(f"Detected encoding: {result['encoding']}")
    print(f"Confidence: {result['confidence']}")
    
    # Print first 10 bytes in hex
    first_bytes = raw_data[:10]
    print(f"First 10 bytes (hex): {binascii.hexlify(first_bytes)}")
    
    # Print first 10 characters as decoded text
    try:
        decoded_text = raw_data[:10].decode(result['encoding'] or 'utf-8')
        print(f"First 10 characters: {repr(decoded_text)}")
    except Exception as e:
        print(f"Error decoding: {str(e)}")

if __name__ == "__main__":
    check_file_encoding("utils/legal_journey.py")
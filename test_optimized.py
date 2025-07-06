import os
import tempfile
from pathlib import Path
from bitpaper.core import BitPaperEncoder, BitPaperDecoder

def test_optimized_encoding():
    print("🧪 Testing Optimized BitPaper Encoding")
    print("=" * 50)
    
    # Create test data
    test_data = b"This is a test file for optimized BitPaper encoding. " * 100
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        print(f"Original file size: {len(test_data)} bytes")
        
        # Test simple mode
        encoder = BitPaperEncoder(pretty_mode=False)
        pages, metadata = encoder.file_to_bitstream_pages(test_file)
        
        print(f"Encoded into {len(pages)} pages")
        print(f"Total bits: {sum(len(page) for page in pages)}")
        print(f"Compression ratio: {len(test_data) / (sum(len(page) for page in pages) / 8):.2f}x")
        
        # Test pretty mode
        encoder_pretty = BitPaperEncoder(pretty_mode=True)
        pages_pretty, metadata_pretty = encoder_pretty.file_to_bitstream_pages(test_file)
        
        print(f"Pretty mode: {len(pages_pretty)} pages")
        print(f"Pretty total bits: {sum(len(page) for page in pages_pretty)}")
        
        # Test decoding
        decoder = BitPaperDecoder(pretty_mode=False)
        decoded_data, decoded_metadata = decoder.bitstream_to_data(''.join(pages))
        
        print(f"Decoded size: {len(decoded_data)} bytes")
        print(f"Data match: {decoded_data == test_data}")
        print(f"Metadata: {decoded_metadata}")
        
        return True
        
    finally:
        os.unlink(test_file)

if __name__ == "__main__":
    test_optimized_encoding() 
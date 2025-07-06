import os
import time
from pathlib import Path
from bitpaper.core import BitPaperEncoder, BitPaperDecoder

def test_real_files():
    print("📁 Testing Optimized BitPaper with Real Files")
    print("=" * 50)
    
    # Create test files
    test_files = {
        'small.txt': b"This is a small test file for BitPaper optimization testing.",
        'medium.txt': b"This is a medium-sized test file. " * 100,
        'large.txt': b"This is a large test file for comprehensive testing. " * 1000
    }
    
    for filename, content in test_files.items():
        print(f"\n📄 Testing {filename}:")
        print(f"  Size: {len(content)} bytes")
        
        # Save file
        with open(filename, 'wb') as f:
            f.write(content)
        
        try:
            # Test encoding
            start_time = time.time()
            encoder = BitPaperEncoder(pretty_mode=False)
            pages, metadata = encoder.file_to_bitstream_pages(filename)
            encode_time = time.time() - start_time
            
            total_bits = sum(len(page) for page in pages)
            compression_ratio = len(content) / (total_bits / 8)
            
            print(f"  Encoded: {len(pages)} pages")
            print(f"  Total bits: {total_bits}")
            print(f"  Compression: {compression_ratio:.2f}x")
            print(f"  Encode time: {encode_time:.3f}s")
            
            # Test decoding
            start_time = time.time()
            decoder = BitPaperDecoder(pretty_mode=False)
            decoded_data, decoded_metadata = decoder.bitstream_to_data(''.join(pages))
            decode_time = time.time() - start_time
            
            print(f"  Decoded: {len(decoded_data)} bytes")
            print(f"  Data match: {decoded_data == content}")
            print(f"  Decode time: {decode_time:.3f}s")
            print(f"  Metadata: {decoded_metadata}")
            
        finally:
            os.unlink(filename)

if __name__ == "__main__":
    test_real_files() 
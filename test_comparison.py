import os
import tempfile
from pathlib import Path
from bitpaper.core import BitPaperEncoder, BitPaperDecoder

def test_comparison():
    print("🔍 Comparing Optimized BitPaper Performance")
    print("=" * 50)
    
    # Create test data of different sizes
    test_sizes = [1000, 10000, 50000, 100000]
    
    for size in test_sizes:
        print(f"\n Testing with {size} bytes:")
        test_data = b"Test data " * (size // 10)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
            f.write(test_data)
            test_file = f.name
        
        try:
            # Test simple mode
            encoder = BitPaperEncoder(pretty_mode=False)
            pages, metadata = encoder.file_to_bitstream_pages(test_file)
            
            total_bits = sum(len(page) for page in pages)
            compression_ratio = len(test_data) / (total_bits / 8)
            
            print(f"  Original: {len(test_data)} bytes")
            print(f"  Encoded: {total_bits} bits ({total_bits//8} bytes)")
            print(f"  Pages: {len(pages)}")
            print(f"  Compression: {compression_ratio:.2f}x")
            print(f"  Efficiency: {(total_bits/8)/len(test_data)*100:.1f}%")
            
            # Test decoding
            decoder = BitPaperDecoder(pretty_mode=False)
            decoded_data, decoded_metadata = decoder.bitstream_to_data(''.join(pages))
            
            print(f"  Decoded: {len(decoded_data)} bytes")
            print(f"  Match: {decoded_data == test_data}")
            
        finally:
            os.unlink(test_file)

if __name__ == "__main__":
    test_comparison() 
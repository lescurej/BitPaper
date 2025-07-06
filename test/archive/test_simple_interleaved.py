import os
import tempfile
import time
from pathlib import Path
from bitpaper.interleaved_core import InterleavedBitPaperEncoder, InterleavedBitPaperDecoder

def test_simple_interleaved():
    print("Testing Simple Interleaved BitPaper...")
    
    # Create test data
    test_data = b"Simple test message"
    password = "test_password"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(test_data)
        test_file = f.name
    
    try:
        print(f"Original data size: {len(test_data)} bytes")
        print(f"Original data: {test_data}")
        
        # Encode without error correction for simplicity
        encoder = InterleavedBitPaperEncoder(password, error_correction_level=0.0)
        decoder = InterleavedBitPaperDecoder(password, error_correction_level=0.0)
        
        # Encode
        print("\nEncoding with interleaving...")
        bitstream = encoder.file_to_bitstream(test_file)
        print(f"Encoded bitstream length: {len(bitstream)} bits")
        
        img = encoder.bitstream_to_image(bitstream)
        print(f"Generated image size: {img.size}")
        
        # Decode
        print("\nDecoding with deinterleaving...")
        decoded_bitstream = decoder.image_to_bitstream(img, len(bitstream))
        print(f"Decoded bitstream length: {len(decoded_bitstream)} bits")
        
        decoded_data = decoder.bitstream_to_data(decoded_bitstream)
        print(f"Decoded data size: {len(decoded_data)} bytes")
        print(f"Decoded data: {decoded_data}")
        
        # Verify
        if test_data == decoded_data:
            print("\n✓ Simple interleaved data matches perfectly!")
            return True
        else:
            print("\n✗ Simple interleaved data mismatch")
            return False
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.unlink(test_file)

if __name__ == "__main__":
    print("=== Simple Interleaved BitPaper Test ===\n")
    
    success = test_simple_interleaved()
    
    if success:
        print("\n✓ Simple interleaved test passed!")
    else:
        print("\n❌ Simple interleaved test failed.") 